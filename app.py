#!/usr/bin/env python3
"""
School Campus Check-In System
=============================
Full local web app for tracking who enters and leaves campus.

- Roles: admin, teacher, student, staff
- Check-IN / Check-OUT buttons
- Browser geolocation vs school geofence (lat/lng + radius)
- Live "who is on campus" board
- History + CSV export
- PIN login (simple, local)

Run:
  pip install -r requirements.txt
  python app.py
  open http://localhost:5050
"""

import csv
import hashlib
import io
import math
import sqlite3
import secrets
from datetime import datetime, date
from functools import wraps
from pathlib import Path

from flask import (
    Flask, request, session, redirect, url_for,
    render_template_string, g, Response, jsonify
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
DB_PATH = Path(__file__).parent / "campus.db"

# Default school geofence (change in Admin → Settings or below)
DEFAULT_SCHOOL = {
    "name": "Demo High School",
    "lat": 40.7128,      # example: change to your school
    "lng": -74.0060,
    "radius_m": 150,     # meters
}

# ---------- db ----------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        pin_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin','teacher','student','staff')),
        active INTEGER DEFAULT 1,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        event_type TEXT NOT NULL CHECK(event_type IN ('in','out')),
        lat REAL,
        lng REAL,
        accuracy_m REAL,
        inside_geofence INTEGER,
        note TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    # seed settings
    for k, v in [
        ("school_name", DEFAULT_SCHOOL["name"]),
        ("school_lat", str(DEFAULT_SCHOOL["lat"])),
        ("school_lng", str(DEFAULT_SCHOOL["lng"])),
        ("school_radius_m", str(DEFAULT_SCHOOL["radius_m"])),
    ]:
        db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", (k, v))

    # seed admin if empty
    n = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if n == 0:
        now = datetime.now().isoformat(timespec="seconds")
        db.execute(
            "INSERT INTO users (name, pin_hash, role, created_at) VALUES (?,?,?,?)",
            ("Admin", hash_pin("0000"), "admin", now)
        )
        db.execute(
            "INSERT INTO users (name, pin_hash, role, created_at) VALUES (?,?,?,?)",
            ("Ms. Rivera", hash_pin("1234"), "teacher", now)
        )
        db.execute(
            "INSERT INTO users (name, pin_hash, role, created_at) VALUES (?,?,?,?)",
            ("Alex Student", hash_pin("1111"), "student", now)
        )
        db.execute(
            "INSERT INTO users (name, pin_hash, role, created_at) VALUES (?,?,?,?)",
            ("Sam Staff", hash_pin("2222"), "staff", now)
        )
    db.commit()
    db.close()

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def get_setting(key, default=""):
    row = get_db().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default

def set_setting(key, value):
    get_db().execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, str(value))
    )
    get_db().commit()

def haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def current_status(user_id):
    """Return 'in' or 'out' based on last event."""
    row = get_db().execute(
        "SELECT event_type FROM events WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    return row["event_type"] if row else "out"

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            return "Admin only", 403
        return f(*args, **kwargs)
    return wrapped

# ---------- templates (single-file app) ----------

BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }} · Campus Check-In</title>
  <style>
    :root {
      --bg: #0f172a; --card: #1e293b; --text: #e2e8f0; --muted: #94a3b8;
      --accent: #38bdf8; --ok: #22c55e; --warn: #f59e0b; --bad: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
    header { background: var(--card); padding: 0.9rem 1.25rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; }
    header a { color: var(--accent); text-decoration: none; margin-left: 1rem; font-size: 0.9rem; }
    .wrap { max-width: 900px; margin: 0 auto; padding: 1.5rem 1rem; }
    .card { background: var(--card); border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; border: 1px solid #334155; }
    h1 { font-size: 1.4rem; margin-bottom: 0.5rem; }
    h2 { font-size: 1.1rem; margin-bottom: 0.75rem; color: var(--accent); }
    .muted { color: var(--muted); font-size: 0.9rem; }
    label { display: block; margin: 0.6rem 0 0.25rem; font-size: 0.85rem; color: var(--muted); }
    input, select { width: 100%; padding: 0.65rem 0.75rem; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: var(--text); font-size: 1rem; }
    button, .btn {
      display: inline-block; padding: 0.75rem 1.25rem; border: none; border-radius: 10px;
      font-weight: 600; font-size: 1rem; cursor: pointer; text-decoration: none; color: #0f172a;
    }
    .btn-in { background: var(--ok); width: 100%; margin-top: 0.75rem; }
    .btn-out { background: var(--warn); width: 100%; margin-top: 0.75rem; }
    .btn-primary { background: var(--accent); }
    .btn-danger { background: var(--bad); color: #fff; }
    .status-in { color: var(--ok); font-weight: 700; }
    .status-out { color: var(--muted); font-weight: 700; }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th, td { padding: 0.5rem 0.4rem; text-align: left; border-bottom: 1px solid #334155; }
    th { color: var(--muted); font-weight: 600; }
    .pill { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
    .pill-in { background: #14532d; color: #86efac; }
    .pill-out { background: #44403c; color: #d6d3d1; }
    .error { background: #450a0a; color: #fecaca; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
    .okmsg { background: #14532d; color: #bbf7d0; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
    .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
    @media (max-width: 600px) { .grid2 { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <div><strong>{{ school_name }}</strong> <span class="muted">Check-In</span></div>
    <nav>
      {% if user %}
        <a href="{{ url_for('dashboard') }}">Home</a>
        <a href="{{ url_for('history') }}">History</a>
        {% if user.role == 'admin' or user.role == 'teacher' %}
          <a href="{{ url_for('campus_board') }}">Who's here</a>
        {% endif %}
        {% if user.role == 'admin' %}
          <a href="{{ url_for('admin') }}">Admin</a>
        {% endif %}
        <a href="{{ url_for('logout') }}">Logout</a>
      {% endif %}
    </nav>
  </header>
  <div class="wrap">
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    {% if msg %}<div class="okmsg">{{ msg }}</div>{% endif %}
    {{ body|safe }}
  </div>
</body>
</html>
"""

def page(title, body, error=None, msg=None):
    user = None
    if "user_id" in session:
        user = get_db().execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return render_template_string(
        BASE,
        title=title,
        body=body,
        error=error,
        msg=msg,
        user=user,
        school_name=get_setting("school_name", "School"),
    )

# ---------- routes ----------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        pin = request.form.get("pin", "").strip()
        row = get_db().execute(
            "SELECT * FROM users WHERE name=? AND active=1", (name,)
        ).fetchone()
        if row and row["pin_hash"] == hash_pin(pin):
            session["user_id"] = row["id"]
            session["role"] = row["role"]
            session["name"] = row["name"]
            return redirect(url_for("dashboard"))
        return page("Login", LOGIN_FORM, error="Wrong name or PIN")
    return page("Login", LOGIN_FORM)

LOGIN_FORM = """
<div class="card" style="max-width:400px;margin:2rem auto">
  <h1>Campus Login</h1>
  <p class="muted">Enter your name and PIN</p>
  <form method="post">
    <label>Name</label>
    <input name="name" required placeholder="e.g. Alex Student" autofocus>
    <label>PIN</label>
    <input name="pin" type="password" required inputmode="numeric" placeholder="4+ digits">
    <button class="btn btn-primary" style="width:100%;margin-top:1rem" type="submit">Login</button>
  </form>
  <p class="muted" style="margin-top:1rem;font-size:0.8rem">
    Demo: Admin/0000 · Ms. Rivera/1234 · Alex Student/1111 · Sam Staff/2222
  </p>
</div>
"""

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["user_id"]
    status = current_status(uid)
    school = get_setting("school_name")
    radius = get_setting("school_radius_m")
    body = f"""
    <div class="card">
      <h1>Hi, {session.get('name')}</h1>
      <p class="muted">Role: {session.get('role')} · {school}</p>
      <p style="margin-top:1rem;font-size:1.2rem">
        Status:
        {'<span class="status-in">ON CAMPUS</span>' if status=='in' else '<span class="status-out">OFF CAMPUS</span>'}
      </p>
    </div>
    <div class="card">
      <h2>Check In / Out</h2>
      <p class="muted">We use your phone GPS to verify you are near the school (within {radius} m).</p>
      <p id="loc-status" class="muted" style="margin:0.5rem 0">Location: waiting…</p>
      <button class="btn btn-in" id="btn-in" onclick="doCheck('in')" disabled>✅ CHECK IN (Enter)</button>
      <button class="btn btn-out" id="btn-out" onclick="doCheck('out')" disabled>🚪 CHECK OUT (Exit)</button>
      <p id="result" style="margin-top:1rem"></p>
    </div>
    <script>
      let lat = null, lng = null, accuracy = null;
      function setReady(ok, msg) {{
        document.getElementById('loc-status').textContent = msg;
        document.getElementById('btn-in').disabled = !ok;
        document.getElementById('btn-out').disabled = !ok;
      }}
      if (!navigator.geolocation) {{
        setReady(false, 'Geolocation not supported on this device');
      }} else {{
        navigator.geolocation.getCurrentPosition(
          (pos) => {{
            lat = pos.coords.latitude;
            lng = pos.coords.longitude;
            accuracy = pos.coords.accuracy;
            setReady(true, 'Location ready (±' + Math.round(accuracy) + ' m)');
          }},
          (err) => setReady(false, 'Location error: ' + err.message),
          {{ enableHighAccuracy: true, timeout: 15000 }}
        );
      }}
      async function doCheck(type) {{
        const res = await fetch('/api/check', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{ type, lat, lng, accuracy }})
        }});
        const data = await res.json();
        const el = document.getElementById('result');
        el.innerHTML = data.ok
          ? '<span style="color:#86efac">' + data.message + '</span>'
          : '<span style="color:#fca5a5">' + data.message + '</span>';
        if (data.ok) setTimeout(() => location.reload(), 1200);
      }}
    </script>
    """
    return page("Home", body)

@app.route("/api/check", methods=["POST"])
@login_required
def api_check():
    data = request.get_json(force=True, silent=True) or {}
    etype = data.get("type")
    if etype not in ("in", "out"):
        return jsonify(ok=False, message="Invalid type"), 400

    try:
        lat = float(data.get("lat"))
        lng = float(data.get("lng"))
        accuracy = float(data.get("accuracy") or 0)
    except (TypeError, ValueError):
        return jsonify(ok=False, message="Location required"), 400

    school_lat = float(get_setting("school_lat"))
    school_lng = float(get_setting("school_lng"))
    radius = float(get_setting("school_radius_m"))
    dist = haversine_m(lat, lng, school_lat, school_lng)
    inside = dist <= radius + max(accuracy, 0)  # allow GPS error margin

    # Policy: must be inside geofence to check IN.
    # Check OUT allowed even slightly outside (walking away).
    if etype == "in" and not inside:
        return jsonify(
            ok=False,
            message=f"You appear {int(dist)} m from school (allowed {int(radius)} m). Move closer and retry."
        )

    status = current_status(session["user_id"])
    if etype == "in" and status == "in":
        return jsonify(ok=False, message="Already checked in.")
    if etype == "out" and status == "out":
        return jsonify(ok=False, message="Already checked out.")

    now = datetime.now().isoformat(timespec="seconds")
    get_db().execute(
        """INSERT INTO events (user_id, event_type, lat, lng, accuracy_m, inside_geofence, created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (session["user_id"], etype, lat, lng, accuracy, 1 if inside else 0, now)
    )
    get_db().commit()

    if etype == "in":
        msg = f"Checked IN at {now[11:16]}. Welcome to campus."
    else:
        msg = f"Checked OUT at {now[11:16]}. See you next time."
    return jsonify(ok=True, message=msg, distance_m=round(dist))

@app.route("/history")
@login_required
def history():
    uid = session["user_id"]
    role = session.get("role")
    db = get_db()
    if role in ("admin", "teacher"):
        rows = db.execute("""
            SELECT e.*, u.name, u.role as urole FROM events e
            JOIN users u ON u.id = e.user_id
            ORDER BY e.id DESC LIMIT 100
        """).fetchall()
    else:
        rows = db.execute("""
            SELECT e.*, u.name, u.role as urole FROM events e
            JOIN users u ON u.id = e.user_id
            WHERE e.user_id=?
            ORDER BY e.id DESC LIMIT 50
        "", (uid,)).fetchall()

    rows_html = ""
    for r in rows:
        pill = "pill-in" if r["event_type"] == "in" else "pill-out"
        label = "IN" if r["event_type"] == "in" else "OUT"
        geo = "✓" if r["inside_geofence"] else "✗"
        rows_html += f"""
        <tr>
          <td>{r['created_at'][5:16]}</td>
          <td>{r['name']}</td>
          <td><span class="pill {pill}">{label}</span></td>
          <td>{geo}</td>
        </tr>"""

    body = f"""
    <div class="card">
      <h2>History</h2>
      <table>
        <tr><th>When</th><th>Who</th><th>Event</th><th>Geo</th></tr>
        {rows_html or '<tr><td colspan="4">No events yet</td></tr>'}
      </table>
    </div>
    """
    return page("History", body)

@app.route("/campus")
@login_required
def campus_board():
    if session.get("role") not in ("admin", "teacher"):
        return "Teachers/Admin only", 403
    db = get_db()
    users = db.execute("SELECT id, name, role FROM users WHERE active=1 ORDER BY name").fetchall()
    on_campus = []
    off_campus = []
    for u in users:
        st = current_status(u["id"])
        if st == "in":
            on_campus.append(u)
        else:
            off_campus.append(u)

    def list_users(lst):
        if not lst:
            return "<p class='muted'>None</p>"
        return "<ul>" + "".join(f"<li>{u['name']} <span class='muted'>({u['role']})</span></li>" for u in lst) + "</ul>"

    body = f"""
    <div class="grid2">
      <div class="card">
        <h2>🟢 On campus ({len(on_campus)})</h2>
        {list_users(on_campus)}
      </div>
      <div class="card">
        <h2>⚪ Off campus ({len(off_campus)})</h2>
        {list_users(off_campus)}
      </div>
    </div>
    """
    return page("Who's here", body)

@app.route("/admin", methods=["GET", "POST"])
@login_required
@admin_required
def admin():
    db = get_db()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "settings":
            set_setting("school_name", request.form.get("school_name", "School"))
            set_setting("school_lat", request.form.get("school_lat", "0"))
            set_setting("school_lng", request.form.get("school_lng", "0"))
            set_setting("school_radius_m", request.form.get("school_radius_m", "150"))
            return page("Admin", admin_body(), msg="Settings saved")
        if action == "add_user":
            name = request.form.get("name", "").strip()
            pin = request.form.get("pin", "").strip()
            role = request.form.get("role", "student")
            if name and pin and role in ("admin", "teacher", "student", "staff"):
                db.execute(
                    "INSERT INTO users (name, pin_hash, role, created_at) VALUES (?,?,?,?)",
                    (name, hash_pin(pin), role, datetime.now().isoformat(timespec="seconds"))
                )
                db.commit()
                return page("Admin", admin_body(), msg=f"Added {name}")
        if action == "deactivate":
            uid = request.form.get("user_id")
            db.execute("UPDATE users SET active=0 WHERE id=?", (uid,))
            db.commit()
            return page("Admin", admin_body(), msg="User deactivated")

    return page("Admin", admin_body())

def admin_body():
    db = get_db()
    users = db.execute("SELECT * FROM users ORDER BY role, name").fetchall()
    urows = ""
    for u in users:
        active = "yes" if u["active"] else "no"
        urows += f"""
        <tr>
          <td>{u['name']}</td><td>{u['role']}</td><td>{active}</td>
          <td>
            <form method="post" style="display:inline">
              <input type="hidden" name="action" value="deactivate">
              <input type="hidden" name="user_id" value="{u['id']}">
              <button class="btn btn-danger" style="padding:0.3rem 0.6rem;font-size:0.8rem" type="submit">Disable</button>
            </form>
          </td>
        </tr>"""

    return f"""
    <div class="card">
      <h2>School geofence</h2>
      <form method="post">
        <input type="hidden" name="action" value="settings">
        <label>School name</label>
        <input name="school_name" value="{get_setting('school_name')}">
        <div class="grid2">
          <div>
            <label>Latitude</label>
            <input name="school_lat" value="{get_setting('school_lat')}">
          </div>
          <div>
            <label>Longitude</label>
            <input name="school_lng" value="{get_setting('school_lng')}">
          </div>
        </div>
        <label>Radius (meters)</label>
        <input name="school_radius_m" value="{get_setting('school_radius_m')}">
        <button class="btn btn-primary" style="margin-top:1rem" type="submit">Save settings</button>
      </form>
      <p class="muted" style="margin-top:0.75rem">Tip: open Google Maps → right‑click school → copy coordinates.</p>
    </div>
    <div class="card">
      <h2>Add user</h2>
      <form method="post">
        <input type="hidden" name="action" value="add_user">
        <label>Name</label><input name="name" required>
        <label>PIN</label><input name="pin" required>
        <label>Role</label>
        <select name="role">
          <option value="student">student</option>
          <option value="teacher">teacher</option>
          <option value="staff">staff</option>
          <option value="admin">admin</option>
        </select>
        <button class="btn btn-primary" style="margin-top:1rem" type="submit">Add</button>
      </form>
    </div>
    <div class="card">
      <h2>Users</h2>
      <table>
        <tr><th>Name</th><th>Role</th><th>Active</th><th></th></tr>
        {urows}
      </table>
      <p style="margin-top:1rem"><a class="btn btn-primary" href="{url_for('export_csv')}">Export events CSV</a></p>
    </div>
    """

@app.route("/export.csv")
@login_required
@admin_required
def export_csv():
    db = get_db()
    rows = db.execute("""
        SELECT e.created_at, u.name, u.role, e.event_type, e.lat, e.lng,
               e.accuracy_m, e.inside_geofence
        FROM events e JOIN users u ON u.id = e.user_id
        ORDER BY e.id
    """).fetchall()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["time", "name", "role", "event", "lat", "lng", "accuracy_m", "inside_geofence"])
    for r in rows:
        w.writerow([r["created_at"], r["name"], r["role"], r["event_type"],
                    r["lat"], r["lng"], r["accuracy_m"], r["inside_geofence"]])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=campus_events.csv"})

if __name__ == "__main__":
    init_db()
    print("School Campus Check-In")
    print("Open http://localhost:5050")
    print("Demo logins: Admin/0000  |  Ms. Rivera/1234  |  Alex Student/1111")
    app.run(host="0.0.0.0", port=5050, debug=True)
