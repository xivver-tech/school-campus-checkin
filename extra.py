"""Extra features with RBAC enforcement."""
from datetime import datetime, date, timedelta
from flask import request, session, redirect, url_for
from rbac import require, has_perm

def register_extra(app, helpers):
    page = helpers["page"]
    tr = helpers["tr"]
    get_db = helpers["get_db"]
    login_required = helpers["login_required"]
    current_status = helpers["current_status"]
    is_late_now = helpers["is_late_now"]

    def ensure_tables():
        db = get_db()
        db.executescript("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            message TEXT NOT NULL,
            created_at TEXT
        );
        """)
        try:
            db.execute("SELECT class_group FROM users LIMIT 1")
        except Exception:
            try:
                db.execute("ALTER TABLE users ADD COLUMN class_group TEXT DEFAULT ''")
                db.commit()
            except Exception:
                pass

    @app.before_request
    def _extra_tables():
        if request.endpoint:
            try:
                ensure_tables()
            except Exception:
                pass

    @app.route("/absent")
    @login_required
    @require("report.view")
    def absent_today():
        today = date.today().isoformat()
        db = get_db()
        students = db.execute(
            "SELECT id, name, role, COALESCE(class_group,'') as class_group FROM users WHERE active=1 AND role='student' ORDER BY name"
        ).fetchall()
        checked = {
            r["user_id"]
            for r in db.execute(
                "SELECT DISTINCT user_id FROM events WHERE event_type='in' AND created_at LIKE ?",
                (today + "%",),
            ).fetchall()
        }
        absents = [s for s in students if s["id"] not in checked]
        rows = "".join(
            f"<tr><td>{s['name']}</td><td>{s['class_group'] or '—'}</td></tr>"
            for s in absents
        )
        body = f"""
        <div class="card">
          <h2>{tr('absent_today')} ({today})</h2>
          <p class="muted">{len(absents)} / {len(students)}</p>
          <table>
            <tr><th>{tr('name')}</th><th>{tr('class_group')}</th></tr>
            {rows or '<tr><td colspan="2">'+tr('no_absent')+'</td></tr>'}
          </table>
        </div>
        <p><a class="btn btn-primary" href="{url_for('manual_check')}">{tr('manual_check')}</a></p>
        """
        return page(tr("absent"), body)

    @app.route("/manual", methods=["GET", "POST"])
    @login_required
    @require("checkin.manual")
    def manual_check():
        db = get_db()
        students = db.execute(
            "SELECT id, name, COALESCE(class_group,'') as class_group FROM users WHERE active=1 AND role IN ('student','staff','busdriver') ORDER BY name"
        ).fetchall()
        msg = None
        if request.method == "POST":
            uid = int(request.form.get("user_id", 0))
            etype = request.form.get("etype", "in")
            reason = request.form.get("reason", "")
            note = request.form.get("note", "")
            if reason and reason != "none":
                note = f"[{reason}] {note}".strip()
            note = (note + " (manual by " + session.get("name", "?") + ")")[:300]
            if etype in ("in", "out") and uid:
                st = current_status(uid)
                if etype == "in" and st == "in":
                    msg = tr("already_in")
                elif etype == "out" and st == "out":
                    msg = tr("already_out")
                else:
                    late = 1 if (etype == "in" and is_late_now()) else 0
                    now = datetime.now().isoformat(timespec="seconds")
                    db.execute(
                        """INSERT INTO events (user_id,event_type,inside_geofence,is_late,note,created_at)
                           VALUES (?,?,1,?,?,?)""",
                        (uid, etype, late, note, now),
                    )
                    db.commit()
                    msg = tr("saved")
        opts = "".join(
            f"<option value='{s['id']}'>{s['name']} {('('+s['class_group']+')') if s['class_group'] else ''}</option>"
            for s in students
        )
        body = f"""
        <div class="card">
          <h2>{tr('manual_check')}</h2>
          <p class="muted">{tr('check_for')}</p>
          <form method="post">
            <label>{tr('name')}</label>
            <select name="user_id" required>{opts}</select>
            <label>{tr('reason')}</label>
            <select name="reason">
              <option value="none">{tr('reason_none')}</option>
              <option value="medical">{tr('reason_medical')}</option>
              <option value="transport">{tr('reason_transport')}</option>
              <option value="family">{tr('reason_family')}</option>
              <option value="other">{tr('reason_other')}</option>
            </select>
            <label>{tr('note')}</label>
            <input name="note" placeholder="{tr('note_ph')}">
            <button class="btn btn-in" name="etype" value="in" type="submit">{tr('do_check_in')}</button>
            <button class="btn btn-out" name="etype" value="out" type="submit">{tr('do_check_out')}</button>
          </form>
        </div>
        """
        return page(tr("manual_check"), body, msg=msg)

    @app.route("/announce", methods=["GET", "POST"])
    @login_required
    @require("announce.read")
    def announce():
        db = get_db()
        ensure_tables()
        if request.method == "POST":
            if not has_perm("announce.post"):
                return "Cannot post announcements", 403
            msg = (request.form.get("message") or "").strip()
            if msg:
                db.execute(
                    "INSERT INTO announcements (author, message, created_at) VALUES (?,?,?)",
                    (session.get("name"), msg[:500], datetime.now().isoformat(timespec="seconds")),
                )
                db.commit()
        rows = db.execute(
            "SELECT * FROM announcements ORDER BY id DESC LIMIT 30"
        ).fetchall()
        list_html = "".join(
            f"<div class='card' style='padding:0.85rem'><strong>{r['author']}</strong>"
            f" <span class='muted'>{r['created_at'][5:16]}</span><p style='margin-top:0.4rem'>{r['message']}</p></div>"
            for r in rows
        )
        form = ""
        if has_perm("announce.post"):
            form = f"""
            <div class="card">
              <h2>{tr('post_announce')}</h2>
              <form method="post">
                <label>{tr('message')}</label>
                <textarea name="message" required></textarea>
                <button class="btn btn-primary" type="submit">{tr('save')}</button>
              </form>
            </div>
            """
        body = form + f"<h2>{tr('announcements')}</h2>" + (list_html or f"<p class='muted'>{tr('none')}</p>")
        return page(tr("announcements"), body)

    @app.route("/week")
    @login_required
    @require("report.view")
    def week_report():
        today = date.today()
        start = today - timedelta(days=today.weekday())
        days = [(start + timedelta(days=i)).isoformat() for i in range(7)]
        db = get_db()
        students = db.execute(
            "SELECT id, name, COALESCE(class_group,'') as class_group FROM users WHERE active=1 AND role='student' ORDER BY name"
        ).fetchall()
        present = {}
        for d in days:
            for r in db.execute(
                "SELECT DISTINCT user_id FROM events WHERE event_type='in' AND created_at LIKE ?",
                (d + "%",),
            ).fetchall():
                present.setdefault(r["user_id"], set()).add(d)
        header = "".join(f"<th>{d[5:]}</th>" for d in days)
        rows = ""
        for s in students:
            cells = ""
            n = 0
            for d in days:
                ok = d in present.get(s["id"], set())
                if ok:
                    n += 1
                cells += f"<td>{'✓' if ok else '—'}</td>"
            rows += f"<tr><td>{s['name']}</td><td class='muted'>{s['class_group']}</td>{cells}<td><strong>{n}</strong></td></tr>"
        body = f"""
        <div class="card">
          <h2>{tr('week_report')}</h2>
          <p class="muted">{days[0]} → {days[-1]}</p>
          <div style="overflow-x:auto">
          <table>
            <tr><th>{tr('name')}</th><th>{tr('class_group')}</th>{header}<th>{tr('present_days')}</th></tr>
            {rows or '<tr><td colspan="10">'+tr('none')+'</td></tr>'}
          </table>
          </div>
        </div>
        """
        return page(tr("week_report"), body)
