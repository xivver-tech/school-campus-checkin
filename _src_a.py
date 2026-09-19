#!/usr/bin/env python3
"""School Campus Check-In - RBAC + lock + Massar link"""
import csv, hashlib, io, math, sqlite3, secrets
from datetime import datetime, date, time as dtime
from functools import wraps
from pathlib import Path
from flask import Flask, request, session, redirect, url_for, render_template_string, g, Response, jsonify
from i18n import I18N
from extra import register_extra
from channels import register_channels
from rbac import require, has_perm, permissions_for_role, current_role
from school_lock import LOCKED_SCHOOL, filter_settings_update, is_appdev
from massar import register_massar

app = Flask(__name__, static_folder="static")
app.secret_key = secrets.token_hex(32)
DB_PATH = Path(__file__).parent / "campus.db"

DEFAULTS = dict(LOCKED_SCHOOL)
DEFAULTS["default_lang"] = "fr"
ALL_ROLES = ("student", "teacher", "staff", "busdriver", "admin", "host", "appdev")

def tr(key):
    L = session.get("lang") or "fr"
    return I18N.get(L, I18N["fr"]).get(key) or I18N["en"].get(key) or key

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH); g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db: db.close()

def hash_pin(pin): return hashlib.sha256(pin.encode()).hexdigest()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, pin_hash TEXT NOT NULL,
        role TEXT NOT NULL, active INTEGER DEFAULT 1, created_at TEXT);
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        event_type TEXT NOT NULL, lat REAL, lng REAL, accuracy_m REAL,
        inside_geofence INTEGER, is_late INTEGER DEFAULT 0, note TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);''')
    try: db.execute("SELECT is_late FROM events LIMIT 1")
    except sqlite3.OperationalError: db.execute("ALTER TABLE events ADD COLUMN is_late INTEGER DEFAULT 0")
    try: db.execute("SELECT class_group FROM users LIMIT 1")
    except sqlite3.OperationalError: db.execute("ALTER TABLE users ADD COLUMN class_group TEXT DEFAULT ''")
    try: db.execute("SELECT code_massar FROM users LIMIT 1")
    except sqlite3.OperationalError: db.execute("ALTER TABLE users ADD COLUMN code_massar TEXT DEFAULT ''")
    for k,v in DEFAULTS.items():
        db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (k,v))
    for k,v in LOCKED_SCHOOL.items():
        db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (k,v))
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0]==0:
        now = datetime.now().isoformat(timespec="seconds")
        for name,pin,role in [("Admin","0000","admin"),("Teacher Demo","1234","teacher"),
            ("Student Demo","1111","student"),("Staff Demo","2222","staff"),
            ("Bus Demo","3333","busdriver"),("Host Demo","4444","host"),
            ("AppDev","9999","appdev")]:
            db.execute("INSERT INTO users (name,pin_hash,role,created_at) VALUES (?,?,?,?)",
                       (name, hash_pin(pin), role, now))
    try:
        db.execute("UPDATE users SET code_massar='R100000001' WHERE name='Student Demo' AND (code_massar IS NULL OR code_massar='')")
        db.execute("UPDATE users SET code_massar='R100000002' WHERE name='Teacher Demo' AND (code_massar IS NULL OR code_massar='')")
    except Exception:
        pass
    db.commit(); db.close()

def get_setting(key, default=""):
    if key in LOCKED_SCHOOL and not is_appdev(session.get("role") if session else ""):
        return LOCKED_SCHOOL[key]
    row = get_db().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else (LOCKED_SCHOOL.get(key) or default)

def set_setting(key, value):
    if key in LOCKED_SCHOOL and not is_appdev(session.get("role") if session else ""):
        return
    get_db().execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (key, str(value)))
    get_db().commit()

def haversine_m(lat1,lng1,lat2,lng2):
    R=6371000.0; p1,p2=math.radians(lat1),math.radians(lat2)
    dp,dl=math.radians(lat2-lat1),math.radians(lng2-lng1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def current_status(uid):
    row=get_db().execute("SELECT event_type FROM events WHERE user_id=? ORDER BY id DESC LIMIT 1",(uid,)).fetchone()
    return row["event_type"] if row else "out"

def last_event(uid):
    return get_db().execute("SELECT * FROM events WHERE user_id=? ORDER BY id DESC LIMIT 1",(uid,)).fetchone()

def is_late_now():
    try:
        h,m=map(int, get_setting("late_after","08:15").split(":"))
        return datetime.now().time()>dtime(h,m)
    except Exception: return False

def login_required(f):
    @wraps(f)
    def w(*a,**k):
        if "user_id" not in session: return redirect(url_for("login"))
        return f(*a,**k)
    return w

def staff_required(f):
    @wraps(f)
    def w(*a,**k):
        if "user_id" not in session: return redirect(url_for("login"))
        if not (has_perm("campus.board") or has_perm("report.view")):
            return tr("staff_only"), 403
        return f(*a,**k)
    return w

def admin_required(f):
    @wraps(f)
    def w(*a,**k):
        if "user_id" not in session: return redirect(url_for("login"))
        if not has_perm("admin.settings"):
            return tr("admin_only"), 403
        return f(*a,**k)
    return w
