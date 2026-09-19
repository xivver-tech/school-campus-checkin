"""
Massar link — one-tap open official portal (no login scrape).
Students → Moutamadris | Teachers → Massar Service
"""
from flask import request, session, redirect, url_for

# Official portals (open in browser / system browser from the app)
URL_STUDENT = "https://moutamadris.men.gov.ma/"
URL_TEACHER = "https://massarservice.men.gov.ma/"
URL_PARENT = "https://massarservice.men.gov.ma/"

def portal_for_role(role: str) -> tuple:
    role = (role or "").lower()
    if role == "student":
        return URL_STUDENT, "Go to Massar (Moutamadris)", "Notes, absences, timetable"
    if role in ("teacher", "admin", "appdev", "staff", "host"):
        return URL_TEACHER, "Go to Massar (enseignants)", "Notes, classes, official absences"
    return URL_TEACHER, "Go to Massar", "Official MEN portal"

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
            db.execute("UPDATE users SET code_massar=? WHERE id=?", (code, uid))
            db.commit()
            msg = "Code Massar saved"
            user = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

        code = ""
        if user:
            try:
                code = user["code_massar"] or ""
            except Exception:
                code = ""

        url, btn_label, subtitle = portal_for_role(role)

        # Huge one-tap button — opens Massar website (or app if phone handles the URL)
        go_btn = f"""
        <div class="card" style="text-align:center;border-color:#38bdf8">
          <p class="muted" style="margin-bottom:0.5rem">{subtitle}</p>
          <a class="btn btn-primary" href="{url}" target="_blank" rel="noopener"
             style="font-size:1.15rem;min-height:56px;background:#0ea5e9">
            {btn_label} ↗
          </a>
          <p class="muted" style="margin-top:0.75rem;font-size:0.8rem">
            Opens the official Massar site in your browser.<br>
            Log in with your Code Massar + password from school.
          </p>
        </div>
        """

        extra_links = ""
        if role == "student":
            extra_links = f"""
            <a class="btn btn-ghost" href="{URL_STUDENT}" target="_blank" rel="noopener">Moutamadris only</a>
            """
        else:
            extra_links = f"""
            <a class="btn btn-ghost" href="{URL_TEACHER}" target="_blank" rel="noopener">Massar Service</a>
            <a class="btn btn-ghost" href="{URL_STUDENT}" target="_blank" rel="noopener">Moutamadris (élève view)</a>
            <a class="btn btn-ghost" href="{url_for('massar_student_codes')}">Student Code Massar list</a>
            """

        body = f"""
        <div class="card">
          <h1>Massar · مسار</h1>
          <p class="muted">One button → official portal. No need to search Google.</p>
        </div>

        {go_btn}

        <div class="card">
          <h2>Your Code Massar (رقم مسار)</h2>
          <form method="post">
            <label>Save it here so you remember</label>
            <input name="code_massar" value="{code}" placeholder="A123456789" maxlength="20">
            <button class="btn btn-ghost" type="submit">Save code</button>
          </form>
          <p class="muted" style="margin-top:0.5rem">From الإدارة / الحارس العام. Login often: code@taalim.ma</p>
        </div>

        <div class="card">
          <h2>More links</h2>
          {extra_links}
        </div>

        <div class="card">
          <p class="muted" style="line-height:1.5;font-size:0.85rem">
            <strong>This campus app</strong> = GPS check-in + class channels.<br>
            <strong>Massar</strong> = official notes (Ministry).<br>
            The button only opens Massar — it does not copy your password.
          </p>
        </div>
        """
        return page("Massar", body, msg=msg)

    @app.route("/massar/go")
    @login_required
    def massar_go():
        """Redirect straight to the right Massar portal for this role."""
        url, _, _ = portal_for_role(session.get("role", ""))
        return redirect(url)

    @app.route("/massar/students")
    @login_required
    def massar_student_codes():
        role = session.get("role")
        if role not in ("teacher", "admin", "appdev", "staff", "host"):
            return "Staff only", 403
        ensure()
        rows = get_db().execute(
            "SELECT name, COALESCE(code_massar,'') as code_massar, COALESCE(class_group,'') as class_group "
            "FROM users WHERE active=1 AND role='student' ORDER BY name"
        ).fetchall()
        trs = "".join(
            f"<tr><td>{r['name']}</td><td>{r['class_group'] or '—'}</td>"
            f"<td><code>{r['code_massar'] or '—'}</code></td></tr>"
            for r in rows
        )
        url, btn, _ = portal_for_role("teacher")
        body = f"""
        <div class="card">
          <a class="btn btn-primary" href="{url}" target="_blank" rel="noopener">{btn} ↗</a>
        </div>
        <div class="card">
          <h2>Student codes</h2>
          <table>
            <tr><th>Name</th><th>Class</th><th>Code Massar</th></tr>
            {trs or '<tr><td colspan="3">—</td></tr>'}
          </table>
          <a class="btn btn-ghost" href="{url_for('massar_hub')}">Back</a>
        </div>
        """
        return page("Code Massar", body)
