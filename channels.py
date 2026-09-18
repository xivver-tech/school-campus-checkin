"""
Class channels for Rowad Nahda Campus.
- Teacher owns multiple class channels (e.g. 8 classes, 900+ students total)
- Students only see channels they belong to (not whole-school feed)
- Posts: homework, after-hours exercises, class notices
"""
from datetime import datetime
from flask import request, session, redirect, url_for

# Expanded roles used across the app
ROLES = (
    "student",
    "teacher",
    "staff",
    "busdriver",
    "admin",
    "host",
    "appdev",
)

STAFF_ROLES = ("admin", "teacher", "staff", "host", "appdev")  # can see campus tools
TEACHER_LIKE = ("admin", "teacher")  # can create class channels & post

def register_channels(app, helpers):
    page = helpers["page"]
    tr = helpers["tr"]
    get_db = helpers["get_db"]
    login_required = helpers["login_required"]

    def ensure():
        db = get_db()
        db.executescript("""
        CREATE TABLE IF NOT EXISTS class_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            description TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            created_at TEXT,
            FOREIGN KEY(teacher_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS channel_members (
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (channel_id, user_id),
            FOREIGN KEY(channel_id) REFERENCES class_channels(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS channel_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            author_name TEXT,
            body TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY(channel_id) REFERENCES class_channels(id)
        );
        """)
        db.commit()

    def my_channels(uid, role):
        db = get_db()
        if role in TEACHER_LIKE:
            # Teachers: channels they own + admin sees all
            if role == "admin":
                return db.execute(
                    "SELECT c.*, u.name as teacher_name FROM class_channels c "
                    "JOIN users u ON u.id=c.teacher_id WHERE c.active=1 ORDER BY c.name"
                ).fetchall()
            return db.execute(
                "SELECT c.*, u.name as teacher_name FROM class_channels c "
                "JOIN users u ON u.id=c.teacher_id WHERE c.active=1 AND c.teacher_id=? ORDER BY c.name",
                (uid,),
            ).fetchall()
        # Students & others: only channels they are members of
        return db.execute(
            "SELECT c.*, u.name as teacher_name FROM class_channels c "
            "JOIN channel_members m ON m.channel_id=c.id "
            "JOIN users u ON u.id=c.teacher_id "
            "WHERE c.active=1 AND m.user_id=? ORDER BY c.name",
            (uid,),
        ).fetchall()

    def can_post(channel_id, uid, role):
        if role == "admin":
            return True
        row = get_db().execute(
            "SELECT teacher_id FROM class_channels WHERE id=? AND active=1", (channel_id,)
        ).fetchone()
        return row and row["teacher_id"] == uid

    def is_member_or_owner(channel_id, uid, role):
        if role == "admin":
            return True
        db = get_db()
        ch = db.execute("SELECT teacher_id FROM class_channels WHERE id=?", (channel_id,)).fetchone()
        if ch and ch["teacher_id"] == uid:
            return True
        m = db.execute(
            "SELECT 1 FROM channel_members WHERE channel_id=? AND user_id=?", (channel_id, uid)
        ).fetchone()
        return bool(m)

    @app.before_request
    def _ch_tables():
        try:
            ensure()
        except Exception:
            pass

    @app.route("/channels")
    @login_required
    def channels_list():
        uid, role = session["user_id"], session.get("role")
        chans = my_channels(uid, role)
        cards = ""
        for c in chans:
            n = get_db().execute(
                "SELECT COUNT(*) AS n FROM channel_members WHERE channel_id=?", (c["id"],)
            ).fetchone()["n"]
            cards += f"""
            <a class="card" href="{url_for('channel_view', cid=c['id'])}" style="display:block;text-decoration:none;color:inherit">
              <h2 style="margin:0">{c['name']}</h2>
              <p class="muted">{c['teacher_name']} · {n} {tr('students') if False else 'students'}</p>
              <p class="muted">{c['description'] or ''}</p>
            </a>"""
        create = ""
        if role in TEACHER_LIKE:
            create = f"""
            <div class="card">
              <h2>{tr('new_channel') if False else 'New class channel'}</h2>
              <form method="post" action="{url_for('channel_create')}">
                <label>Name (e.g. 3A Maths)</label>
                <input name="name" required placeholder="3A">
                <label>Description</label>
                <input name="description" placeholder="After-hours exercises, homework...">
                <button class="btn btn-primary" type="submit">Create</button>
              </form>
            </div>"""
        body = create + f"<h2>Class channels</h2>" + (cards or f"<p class='muted'>{tr('none')}</p>")
        body += f"""<p class="muted" style="margin-top:1rem">Students only see their class channels — not the whole school.</p>"""
        return page("Channels", body)

    @app.route("/channels/create", methods=["POST"])
    @login_required
    def channel_create():
        if session.get("role") not in TEACHER_LIKE:
            return "Forbidden", 403
        name = (request.form.get("name") or "").strip()[:80]
        desc = (request.form.get("description") or "").strip()[:200]
        if name:
            get_db().execute(
                "INSERT INTO class_channels (name, teacher_id, description, created_at) VALUES (?,?,?,?)",
                (name, session["user_id"], desc, datetime.now().isoformat(timespec="seconds")),
            )
            get_db().commit()
        return redirect(url_for("channels_list"))

    @app.route("/channels/<int:cid>", methods=["GET", "POST"])
    @login_required
    def channel_view(cid):
        uid, role = session["user_id"], session.get("role")
        if not is_member_or_owner(cid, uid, role):
            return "This channel is only for its class members.", 403
        db = get_db()
        ch = db.execute(
            "SELECT c.*, u.name as teacher_name FROM class_channels c JOIN users u ON u.id=c.teacher_id WHERE c.id=?",
            (cid,),
        ).fetchone()
        if not ch:
            return "Not found", 404

        # Post message (teacher/admin only)
        if request.method == "POST" and can_post(cid, uid, role):
            body_txt = (request.form.get("body") or "").strip()[:1000]
            if body_txt:
                db.execute(
                    "INSERT INTO channel_posts (channel_id, author_id, author_name, body, created_at) VALUES (?,?,?,?,?)",
                    (cid, uid, session.get("name"), body_txt, datetime.now().isoformat(timespec="seconds")),
                )
                db.commit()

        posts = db.execute(
            "SELECT * FROM channel_posts WHERE channel_id=? ORDER BY id DESC LIMIT 50", (cid,)
        ).fetchall()
        members = db.execute(
            "SELECT u.id, u.name, u.role FROM channel_members m JOIN users u ON u.id=m.user_id "
            "WHERE m.channel_id=? ORDER BY u.name", (cid,)
        ).fetchall()

        posts_html = "".join(
            f"<div class='card' style='padding:0.85rem'><strong>{p['author_name']}</strong> "
            f"<span class='muted'>{p['created_at'][5:16]}</span>"
            f"<p style='margin-top:0.4rem;white-space:pre-wrap'>{p['body']}</p></div>"
            for p in posts
        ) or f"<p class='muted'>{tr('none')}</p>"

        post_form = ""
        if can_post(cid, uid, role):
            post_form = f"""
            <div class="card">
              <h2>Post to class (homework / exercises)</h2>
              <form method="post">
                <textarea name="body" required placeholder="After-hours exercise, homework..."></textarea>
                <button class="btn btn-primary" type="submit">Post</button>
              </form>
            </div>"""

        manage = ""
        if can_post(cid, uid, role):
            # Add student by name
            students = db.execute(
                "SELECT id, name FROM users WHERE active=1 AND role='student' ORDER BY name"
            ).fetchall()
            opts = "".join(f"<option value='{s['id']}'>{s['name']}</option>" for s in students)
            mem_list = "".join(f"<li>{m['name']}</li>" for m in members) or f"<li class='muted'>{tr('none')}</li>"
            manage = f"""
            <div class="card">
              <h2>Members ({len(members)})</h2>
              <ul style="margin-bottom:0.75rem">{mem_list}</ul>
              <form method="post" action="{url_for('channel_add_member', cid=cid)}">
                <label>Add student</label>
                <select name="user_id">{opts}</select>
                <button class="btn btn-primary" type="submit">Add to class</button>
              </form>
            </div>"""

        body = f"""
        <div class="card">
          <h1>{ch['name']}</h1>
          <p class="muted">{ch['teacher_name']} · {ch['description'] or ''}</p>
          <a class="btn btn-ghost" href="{url_for('channels_list')}">All my channels</a>
        </div>
        {post_form}
        <h2>Messages</h2>
        {posts_html}
        {manage}
        """
        return page(ch["name"], body)

    @app.route("/channels/<int:cid>/add", methods=["POST"])
    @login_required
    def channel_add_member(cid):
        uid, role = session["user_id"], session.get("role")
        if not can_post(cid, uid, role):
            return "Forbidden", 403
        try:
            sid = int(request.form.get("user_id", 0))
        except ValueError:
            sid = 0
        if sid:
            try:
                get_db().execute(
                    "INSERT OR IGNORE INTO channel_members (channel_id, user_id) VALUES (?,?)",
                    (cid, sid),
                )
                get_db().commit()
            except Exception:
                pass
        return redirect(url_for("channel_view", cid=cid))
