"""
Massar (MEN Morocco) integration helpers
=======================================
Official system: Ministry of National Education.
We do NOT log into or scrape Massar (no unofficial API).

What this module does:
- Store each user's Code Massar (رقم مسار)
- Show role-based links to official portals
- Students → Moutamadris | Parents hint → Waliye | Teachers → Moudaris info
"""
from flask import request, session, redirect, url_for

# Official MEN portals (public entry points)
MASSAR_PORTALS = {
    "service": "https://massarservice.men.gov.ma/",
    "moutamadris": "https://moutamadris.men.gov.ma/",  # students
    "waliye": "https://massarservice.men.gov.ma/",     # parents (Waliye space)
    "info": "https://www.men.gov.ma/",
}

def register_massar(app, helpers):
    page = helpers["page"]
    tr = helpers["tr"]
    get_db = helpers["get_db"]
    login_required = helpers["login_required"]

    def ensure():
        db = get_db()
        try:
            db.execute("SELECT code_massar FROM users LIMIT 1")
        except Exception:
            try:
                db.execute("ALTER TABLE users ADD COLUMN code_massar TEXT DEFAULT ''")
                db.commit()
            except Exception:
                pass

    @app.before_request
    def _massar_col():
        try:
            ensure()
        except Exception:
            pass

    @app.route("/massar", methods=["GET", "POST"])
    @login_required
    def massar_hub():
        ensure()
        db = get_db()
        uid = session["user_id"]
        role = session.get("role", "")
        user = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        msg = None

        if request.method == "POST":
            code = (request.form.get("code_massar") or "").strip()[:20]
            # Basic format: letter + digits often, keep flexible
            db.execute("UPDATE users SET code_massar=? WHERE id=?", (code, uid))
            db.commit()
            msg = "Code Massar saved"
            user = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

        code = (user["code_massar"] if user and "code_massar" in user.keys() else "") or ""

        # Role-specific guidance
        if role == "student":
            portal_title = "Moutamadris (élève)"
            portal_url = MASSAR_PORTALS["moutamadris"]
            tips = """
            <ul class="muted" style="margin:0.5rem 0 0 1.1rem;line-height:1.6">
              <li>Use your <strong>Code Massar</strong> + password from the school</li>
              <li>Often login looks like: <code>YOURCODE@taalim.ma</code></li>
              <li>See notes, absences, timetable on the official site</li>
            </ul>"""
        elif role in ("teacher", "admin", "appdev", "staff", "host"):
            portal_title = "Massar Service / Moudaris (enseignants)"
            portal_url = MASSAR_PORTALS["service"]
            tips = """
            <ul class="muted" style="margin:0.5rem 0 0 1.1rem;line-height:1.6">
              <li>Teachers enter <strong>notes</strong> and <strong>absences</strong> in official Massar</li>
              <li>This campus app tracks <strong>GPS check-in</strong> separately</li>
              <li>You can copy Code Massar from student profiles (admin)</li>
            </ul>"""
        else:
            portal_title = "Massar Service"
            portal_url = MASSAR_PORTALS["service"]
            tips = "<p class='muted'>Official MEN school system.</p>"

        body = f"""
        <div class="card">
          <h1>Massar · مسار</h1>
          <p class="muted">Ministry of National Education (official). This app does not replace Massar.</p>
        </div>

        <div class="card">
          <h2>Your Code Massar</h2>
          <form method="post">
            <label>رقم مسار / Code Massar</label>
            <input name="code_massar" value="{code}" placeholder="e.g. A123456789" maxlength="20">
            <button class="btn btn-primary" type="submit">Save</button>
          </form>
          <p class="muted" style="margin-top:0.6rem">Get this code from school administration (الحارس / الإدارة).</p>
        </div>

        <div class="card">
          <h2>{portal_title}</h2>
          {tips}
          <a class="btn btn-primary" href="{portal_url}" target="_blank" rel="noopener">Open official Massar</a>
          <a class="btn btn-ghost" href="{MASSAR_PORTALS['moutamadris']}" target="_blank" rel="noopener">Moutamadris (students)</a>
        </div>

        <div class="card">
          <h2>How it connects to this app</h2>
          <p class="muted" style="line-height:1.55">
            <strong>This app:</strong> GPS check-in, class channels, campus board.<br>
            <strong>Massar:</strong> official notes, national absences, exams.<br><br>
            Teachers: use both — check-in here, grades on Massar.<br>
            Students: check-in here, notes on Moutamadris.
          </p>
        </div>
        """
        return page("Massar", body, msg=msg)

    @app.route("/massar/students")
    @login_required
    def massar_student_codes():
        """Staff/teachers: list student Code Massar for reference."""
        role = session.get("role")
        if role not in ("teacher", "admin", "appdev", "staff", "host"):
            return "Staff only", 403
        ensure()
        rows = get_db().execute(
            "SELECT name, role, COALESCE(code_massar,'') as code_massar, COALESCE(class_group,'') as class_group "
            "FROM users WHERE active=1 AND role='student' ORDER BY name"
        ).fetchall()
        trs = "".join(
            f"<tr><td>{r['name']}</td><td>{r['class_group'] or '—'}</td>"
            f"<td><code>{r['code_massar'] or '—'}</code></td></tr>"
            for r in rows
        )
        body = f"""
        <div class="card">
          <h2>Student Code Massar</h2>
          <p class="muted">For reference when working with official Massar. Codes are entered by each student on /massar.</p>
          <table>
            <tr><th>Name</th><th>Class</th><th>Code Massar</th></tr>
            {trs or '<tr><td colspan="3">No students</td></tr>'}
          </table>
          <a class="btn btn-ghost" href="{url_for('massar_hub')}">Back to Massar hub</a>
        </div>
        """
        return page("Code Massar list", body)
