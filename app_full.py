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

BASE='''<!DOCTYPE html><html lang="{{ lang_code|default('fr') }}" dir="{{ 'rtl' if (lang_code|default('fr'))=='ar' else 'ltr' }}"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="theme-color" content="#0f172a"><title>{{ title }} - Campus</title>
<style>
:root{--bg:#0f172a;--card:#1e293b;--text:#e2e8f0;--muted:#94a3b8;--accent:#38bdf8;--ok:#22c55e;--warn:#f59e0b;--bad:#ef4444;--safe:env(safe-area-inset-bottom,0px)}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:system-ui,Tahoma,sans-serif;background:var(--bg);color:var(--text);min-height:100dvh;padding-bottom:calc(72px + var(--safe))}
header{position:sticky;top:0;z-index:20;background:rgba(30,41,59,.95);padding:.75rem 1rem;border-bottom:1px solid #334155;display:flex;justify-content:space-between;align-items:center;gap:.5rem;flex-wrap:wrap}
.brand{font-weight:700;font-size:.85rem}.wrap{max-width:560px;margin:0 auto;padding:1rem}
.card{background:var(--card);border-radius:16px;padding:1.15rem;margin-bottom:.9rem;border:1px solid #334155}
h1{font-size:1.3rem}h2{font-size:1.05rem;margin-bottom:.7rem;color:var(--accent)}
.muted{color:var(--muted);font-size:.88rem}label{display:block;margin:.55rem 0 .25rem;font-size:.82rem;color:var(--muted)}
input,select,textarea{width:100%;padding:.85rem;border-radius:12px;border:1px solid #334155;background:#0f172a;color:var(--text);font-size:16px}
input[readonly]{opacity:.7;border-color:#475569}
button,.btn{display:inline-flex;align-items:center;justify-content:center;padding:1rem;border:none;border-radius:14px;font-weight:700;font-size:1.05rem;cursor:pointer;text-decoration:none;color:#0f172a;width:100%;margin-top:.65rem;min-height:52px}
.btn-in{background:var(--ok)}.btn-out{background:var(--warn)}.btn-primary{background:var(--accent)}.btn-danger{background:var(--bad);color:#fff}.btn-ghost{background:transparent;border:1px solid #334155;color:var(--text)}.btn:disabled{opacity:.45}
.status-in{color:var(--ok);font-weight:800}.status-out{color:var(--muted);font-weight:800}.status-late{color:var(--bad);font-weight:700}
table{width:100%;border-collapse:collapse;font-size:.88rem}th,td{padding:.55rem .3rem;text-align:start;border-bottom:1px solid #334155}th{color:var(--muted)}
.pill{display:inline-block;padding:.2rem .55rem;border-radius:999px;font-size:.72rem;font-weight:700}
.pill-in{background:#14532d;color:#86efac}.pill-out{background:#44403c;color:#d6d3d1}.pill-late{background:#7f1d1d;color:#fecaca}
.error{background:#450a0a;color:#fecaca;padding:.85rem;border-radius:12px;margin-bottom:.9rem}.okmsg{background:#14532d;color:#bbf7d0;padding:.85rem;border-radius:12px;margin-bottom:.9rem}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:.75rem}.stat{text-align:center;padding:.75rem;background:#0f172a;border-radius:12px}.stat-n{font-size:1.6rem;font-weight:800;color:var(--accent)}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;z-index:30;background:rgba(30,41,59,.97);border-top:1px solid #334155;display:flex;justify-content:space-around;padding:.4rem .5rem calc(.4rem + var(--safe))}
.bottom-nav a{flex:1;text-align:center;text-decoration:none;color:var(--muted);font-size:.65rem;padding:.3rem;font-weight:600}.bottom-nav .ico{font-size:1.15rem;display:block}
.loc-bar{display:flex;align-items:center;gap:.5rem;padding:.6rem;background:#0f172a;border-radius:10px;margin:.5rem 0;font-size:.85rem}
.dot{width:10px;height:10px;border-radius:50%;background:var(--muted)}.dot.on{background:var(--ok)}.dot.err{background:var(--bad)}
.lang a{color:#94a3b8;text-decoration:none;font-size:.75rem;padding:.2rem .45rem;border:1px solid #334155;border-radius:6px;margin-inline-start:.25rem}
.lock-banner{background:#422006;color:#fdba74;padding:.75rem;border-radius:12px;margin-bottom:.9rem;font-size:.85rem}
@media(min-width:700px){body{padding-bottom:1rem}.bottom-nav{display:none}header nav.desk{display:flex;flex-wrap:wrap}header nav.desk a{color:var(--accent);text-decoration:none;margin-inline-start:.5rem;font-size:.78rem}}
@media(max-width:699px){header nav.desk{display:none}.grid2{grid-template-columns:1fr}}
</style></head><body>
<header>
<div class="brand">{{ school_name }}</div>
<div class="lang"><a href="/lang/fr">FR</a><a href="/lang/ar">AR</a><a href="/lang/en">EN</a></div>
<nav class="desk">{% if user %}
<a href="{{ url_for('dashboard') }}">{{ tr.home }}</a>
<a href="{{ url_for('history') }}">{{ tr.history }}</a>
<a href="/channels">Channels</a>
<a href="/massar">Massar</a>
{% if user.role in ['admin','teacher','staff','host','appdev'] %}
<a href="{{ url_for('campus_board') }}">{{ tr.campus }}</a><a href="/absent">{{ tr.absent }}</a>
{% endif %}
<a href="/announce">{{ tr.announcements }}</a>
{% if user.role in ['admin','appdev'] %}<a href="{{ url_for('admin') }}">{{ tr.admin }}</a>{% endif %}
<a href="{{ url_for('logout') }}">{{ tr.logout }}</a>{% endif %}</nav>
</header>
<div class="wrap">{% if error %}<div class="error">{{ error }}</div>{% endif %}{% if msg %}<div class="okmsg">{{ msg }}</div>{% endif %}{{ body|safe }}</div>
{% if user %}<nav class="bottom-nav">
<a href="{{ url_for('dashboard') }}"><span class="ico">🏠</span>{{ tr.home }}</a>
<a href="/channels"><span class="ico">📚</span>Class</a>
<a href="/massar"><span class="ico">🎓</span>Massar</a>
<a href="{{ url_for('history') }}"><span class="ico">📋</span>{{ tr.history }}</a>
</nav>{% endif %}
</body></html>'''

class TrObj:
    def __getattr__(self, k): return tr(k)

def page(title, body, error=None, msg=None):
    user=None
    if "user_id" in session:
        user=get_db().execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone()
    return render_template_string(BASE, title=title, body=body, error=error, msg=msg, user=user,
        school_name=get_setting("school_name","School"), lang_code=session.get("lang","fr"), tr=TrObj())

@app.route("/lang/<code>")
def set_lang(code):
    if code in I18N: session["lang"] = code
    return redirect(request.referrer or url_for("index"))

@app.route("/sw.js")
def sw():
    return Response("self.addEventListener('install',e=>self.skipWaiting());", mimetype="application/javascript")

@app.route("/")
def index():
    return redirect(url_for("dashboard" if "user_id" in session else "login"))

@app.route("/login", methods=["GET","POST"])
def login():
    form=f'''<div class="card" style="margin-top:1.5rem"><h1>{tr("login_title")}</h1>
    <p class="muted">{tr("login_sub")}</p>
    <form method="post"><label>{tr("name")}</label><input name="name" required autofocus>
    <label>{tr("pin")}</label><input name="pin" type="password" required inputmode="numeric">
    <button class="btn btn-primary" type="submit">{tr("login_btn")}</button></form>
    <p class="muted" style="margin-top:1rem;font-size:.75rem">Admin/0000 · Teacher/1234 · Student/1111 · AppDev/9999</p></div>'''
    if request.method=="POST":
        name=request.form.get("name","").strip(); pin=request.form.get("pin","").strip()
        row=get_db().execute("SELECT * FROM users WHERE name=? AND active=1",(name,)).fetchone()
        if row and row["pin_hash"]==hash_pin(pin):
            session.update(user_id=row["id"], role=row["role"], name=row["name"])
            return redirect(url_for("dashboard"))
        return page(tr("login_title"), form, error=tr("wrong_login"))
    return page(tr("login_title"), form)

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    uid=session["user_id"]; status=current_status(uid); le=last_event(uid)
    last_line=""
    if le:
        last_line=f"<p class='muted'>{tr('last')}: <strong>{le['event_type'].upper()}</strong> {le['created_at'][11:16]}"
        if le["is_late"]: last_line+=f" · <span class='status-late'>{tr('late')}</span>"
        last_line+="</p>"
    st = ('<span class="status-in">'+tr("on_campus")+'</span>') if status=='in' else ('<span class="status-out">'+tr("off_campus")+'</span>')
    links = f'''<div class="card">
    <a class="btn btn-primary" href="/massar/go" target="_blank" rel="noopener" style="background:#0ea5e9">Go to Massar portal ↗</a>
    <a class="btn btn-ghost" href="/massar">Massar · مسار</a>
    <a class="btn btn-primary" href="/channels">Class channels</a>
    <a class="btn btn-ghost" href="/announce">{tr("announcements")}</a></div>'''
    if has_perm("report.view") or has_perm("campus.board"):
        links = f'''<div class="card"><h2>Tools</h2>
        <a class="btn btn-primary" href="/massar/go" target="_blank" rel="noopener" style="background:#0ea5e9">Go to Massar portal ↗</a>
        <a class="btn btn-ghost" href="/massar">Massar hub</a>
        <a class="btn btn-ghost" href="/massar/students">Code Massar list</a>
        <a class="btn btn-primary" href="/channels">Class channels</a>
        <a class="btn btn-ghost" href="/absent">{tr("absent_today")}</a>
        <a class="btn btn-ghost" href="/manual">{tr("manual_check")}</a>
        <a class="btn btn-ghost" href="/week">{tr("week_report")}</a>
        <a class="btn btn-ghost" href="/announce">{tr("announcements")}</a></div>'''
    body=f'''<div class="card"><h1>{tr("hi")}, {session.get("name")}</h1>
    <p class="muted">{session.get("role")} · {get_setting("school_name")}</p>
    <p style="margin-top:.85rem">{tr("status")}: {st}</p>{last_line}</div>
    <div class="card"><h2>{tr("check_title")}</h2>
    <div class="loc-bar"><span class="dot" id="dot"></span><span id="loc-status">{tr("gps_wait")}</span></div>
    <label>{tr("note")}</label><textarea id="note"></textarea>
    <button class="btn btn-in" id="btn-in" onclick="doCheck('in')" disabled>{tr("check_in")}</button>
    <button class="btn btn-out" id="btn-out" onclick="doCheck('out')" disabled>{tr("check_out")}</button>
    <button class="btn btn-ghost" type="button" onclick="refreshLoc()">{tr("refresh_gps")}</button>
    <p id="result" style="margin-top:.85rem"></p></div>{links}
    <script>
    let lat=null,lng=null,accuracy=null;
    function setReady(ok,msg){{document.getElementById('dot').className='dot '+(ok?'on':'err');
      document.getElementById('loc-status').textContent=msg;
      document.getElementById('btn-in').disabled=!ok;document.getElementById('btn-out').disabled=!ok;}}
    function onPos(pos){{lat=pos.coords.latitude;lng=pos.coords.longitude;accuracy=pos.coords.accuracy;setReady(true,'GPS ±'+Math.round(accuracy)+' m');}}
    function onErr(err){{setReady(false,'GPS: '+err.message);}}
    function refreshLoc(){{setReady(false,'...');navigator.geolocation.getCurrentPosition(onPos,onErr,{{enableHighAccuracy:true,timeout:20000,maximumAge:0}});}}
    if(!navigator.geolocation)setReady(false,'GPS');else{{refreshLoc();navigator.geolocation.watchPosition(onPos,onErr,{{enableHighAccuracy:true,maximumAge:5000}});}}
    async function doCheck(type){{
      document.getElementById('btn-in').disabled=true;document.getElementById('btn-out').disabled=true;
      const res=await fetch('/api/check',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{type,lat,lng,accuracy,note:document.getElementById('note').value}})}});
      const data=await res.json();
      document.getElementById('result').innerHTML=data.ok?'<span style="color:#86efac">'+data.message+'</span>':'<span style="color:#fca5a5">'+data.message+'</span>';
      if(data.ok)setTimeout(()=>location.reload(),1100);else{{document.getElementById('btn-in').disabled=false;document.getElementById('btn-out').disabled=false;}}
    }}
    </script>'''
    return page(tr("home"), body)

@app.route("/api/check", methods=["POST"])
@login_required
@require("checkin.self")
def api_check():
    data=request.get_json(force=True,silent=True) or {}
    etype=data.get("type")
    if etype not in ("in","out"): return jsonify(ok=False,message="Invalid"),400
    try:
        lat,lng,accuracy=float(data["lat"]),float(data["lng"]),float(data.get("accuracy") or 0)
    except (TypeError,ValueError,KeyError):
        return jsonify(ok=False,message=tr("allow_gps")),400
    note=(data.get("note") or "")[:300]
    dist=haversine_m(lat,lng,float(LOCKED_SCHOOL["school_lat"]),float(LOCKED_SCHOOL["school_lng"]))
    radius=float(LOCKED_SCHOOL["school_radius_m"])
    inside=dist<=radius+max(accuracy,0)
    if etype=="in" and not inside:
        return jsonify(ok=False,message=f"{tr('too_far')} ({int(dist)} m)")
    st=current_status(session["user_id"])
    if etype=="in" and st=="in": return jsonify(ok=False,message=tr("already_in"))
    if etype=="out" and st=="out": return jsonify(ok=False,message=tr("already_out"))
    late=1 if (etype=="in" and is_late_now()) else 0
    now=datetime.now().isoformat(timespec="seconds")
    get_db().execute("INSERT INTO events (user_id,event_type,lat,lng,accuracy_m,inside_geofence,is_late,note,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                     (session["user_id"],etype,lat,lng,accuracy,1 if inside else 0,late,note,now))
    get_db().commit()
    msg=f"IN {now[11:16]}. "+(tr("marked_late") if late else tr("welcome")) if etype=="in" else f"OUT {now[11:16]}. "+tr("good_day")
    return jsonify(ok=True,message=msg)

@app.route("/history")
@login_required
def history():
    uid=session["user_id"]
    if has_perm("history.all"):
        rows=get_db().execute("SELECT e.*,u.name FROM events e JOIN users u ON u.id=e.user_id ORDER BY e.id DESC LIMIT 120").fetchall()
    else:
        rows=get_db().execute("SELECT e.*,u.name FROM events e JOIN users u ON u.id=e.user_id WHERE e.user_id=? ORDER BY e.id DESC LIMIT 60",(uid,)).fetchall()
    rows_html=""
    for r in rows:
        pill="pill-in" if r["event_type"]=="in" else "pill-out"
        late=f' <span class="pill pill-late">{tr("late")}</span>' if r["is_late"] else ""
        rows_html+=f'<tr><td>{r["created_at"][5:16]}</td><td>{r["name"]}</td><td><span class="pill {pill}">{r["event_type"].upper()}</span>{late}</td></tr>'
    body=f'<div class="card"><h2>{tr("history_title")}</h2><table><tr><th>{tr("when")}</th><th>{tr("who")}</th><th>{tr("event")}</th></tr>{rows_html or "<tr><td colspan=3>"+tr("none")+"</td></tr>"}</table></div>'
    return page(tr("history"), body)

@app.route("/campus")
@login_required
@require("campus.board")
def campus_board():
    users=get_db().execute("SELECT id,name,role FROM users WHERE active=1 ORDER BY name").fetchall()
    on_c,off_c=[],[]
    for u in users:
        (on_c if current_status(u["id"])=="in" else off_c).append(u)
    def ul(lst):
        if not lst: return "<p class='muted'>"+tr("none")+"</p>"
        return "<ul style='list-style:none'>"+"".join(f"<li>{x['name']} <span class='muted'>({x['role']})</span></li>" for x in lst)+"</ul>"
    body=f'''<div class="grid2"><div class="stat"><div class="stat-n">{len(on_c)}</div><div class="muted">{tr("on_campus_list")}</div></div>
    <div class="stat"><div class="stat-n">{len(off_c)}</div><div class="muted">{tr("off_campus_list")}</div></div></div>
    <div class="card"><h2>{tr("on_campus_list")}</h2>{ul(on_c)}</div>
    <div class="card"><h2>{tr("off_campus_list")}</h2>{ul(off_c)}</div>'''
    return page(tr("campus"), body)

@app.route("/admin", methods=["GET","POST"])
@login_required
@require("admin.settings")
def admin():
    db=get_db()
    if request.method=="POST":
        action=request.form.get("action")
        if action=="settings":
            raw = {k: request.form.get(k) for k in ("school_name","school_lat","school_lng","school_radius_m","school_start","school_end","late_after") if request.form.get(k) is not None}
            allowed = filter_settings_update(raw, session.get("role"))
            for k,v in allowed.items():
                set_setting(k, v)
            if not is_appdev(session.get("role")):
                for k,v in LOCKED_SCHOOL.items():
                    get_db().execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (k,v))
                get_db().commit()
                return page(tr("admin"), admin_body(), msg="School location & hours are LOCKED (appdev only)")
            return page(tr("admin"), admin_body(), msg=tr("save"))
        if action=="add_user" and has_perm("admin.users"):
            name,pin,role=request.form.get("name","").strip(),request.form.get("pin","").strip(),request.form.get("role","student")
            cg=request.form.get("class_group","").strip()
            if name and pin and role in ALL_ROLES:
                try:
                    db.execute("INSERT INTO users (name,pin_hash,role,class_group,created_at) VALUES (?,?,?,?,?)",(name,hash_pin(pin),role,cg,datetime.now().isoformat(timespec="seconds")))
                except Exception:
                    db.execute("INSERT INTO users (name,pin_hash,role,created_at) VALUES (?,?,?,?)",(name,hash_pin(pin),role,datetime.now().isoformat(timespec="seconds")))
                db.commit(); return page(tr("admin"), admin_body(), msg=name)
        if action=="deactivate" and has_perm("admin.users"):
            db.execute("UPDATE users SET active=0 WHERE id=?",(request.form.get("user_id"),)); db.commit()
            return page(tr("admin"), admin_body(), msg=tr("disable"))
        if action=="force_out" and has_perm("admin.force_out"):
            now=datetime.now().isoformat(timespec="seconds"); n=0
            for u in db.execute("SELECT id FROM users WHERE active=1").fetchall():
                if current_status(u["id"])=="in":
                    db.execute("INSERT INTO events (user_id,event_type,inside_geofence,note,created_at) VALUES (?,?,?,?,?)",(u["id"],"out",1,"force",now)); n+=1
            db.commit(); return page(tr("admin"), admin_body(), msg=str(n))
    return page(tr("admin"), admin_body())

def admin_body():
    _ro = "readonly" if not has_perm("admin.school_lock") else ""
    lock_note = ("Editable (appdev)") if has_perm("admin.school_lock") else (
        "LOCKED — GPS & hours fixed for Rowad Nahda Private - Tiznit. Only AppDev can change.")
    users=get_db().execute("SELECT * FROM users ORDER BY role,name").fetchall()
    urows="".join(f'''<tr><td>{u["name"]}</td><td>{u["role"]}</td><td>{"yes" if u["active"] else "no"}</td>
    <td><form method="post" style="display:inline"><input type="hidden" name="action" value="deactivate">
    <input type="hidden" name="user_id" value="{u["id"]}">
    <button class="btn btn-danger" style="min-height:36px;padding:.3rem .5rem;font-size:.75rem;width:auto;margin:0" type="submit">{tr("disable")}</button></form></td></tr>''' for u in users)
    role_opts="".join(f'<option value="{r}">{r}</option>' for r in ALL_ROLES)
    return f'''<div class="lock-banner">{lock_note}</div>
    <div class="card"><h2>{tr("school_hours")}</h2><form method="post"><input type="hidden" name="action" value="settings">
    <label>{tr("name")}</label><input name="school_name" value="{get_setting("school_name")}" {_ro}>
    <div class="grid2"><div><label>{tr("lat")}</label><input name="school_lat" value="{get_setting("school_lat")}" {_ro}></div>
    <div><label>{tr("lng")}</label><input name="school_lng" value="{get_setting("school_lng")}" {_ro}></div></div>
    <label>{tr("radius")}</label><input name="school_radius_m" value="{get_setting("school_radius_m")}" {_ro}>
    <div class="grid2"><div><label>Start</label><input name="school_start" value="{get_setting("school_start")}" {_ro}></div>
    <div><label>End</label><input name="school_end" value="{get_setting("school_end")}" {_ro}></div></div>
    <label>{tr("late_after")}</label><input name="late_after" value="{get_setting("late_after")}" {_ro}>
    <button class="btn btn-primary" type="submit" {"disabled" if _ro else ""}>{tr("save")}</button></form></div>
    <div class="card"><h2>{tr("add_user")}</h2><form method="post"><input type="hidden" name="action" value="add_user">
    <label>{tr("name")}</label><input name="name" required><label>{tr("pin")}</label><input name="pin" required inputmode="numeric">
    <label>{tr("role")}</label><select name="role">{role_opts}</select>
    <label>{tr("class_group")}</label><input name="class_group" placeholder="3A">
    <button class="btn btn-primary" type="submit">{tr("add_user")}</button></form></div>
    <div class="card"><h2>{tr("users")}</h2><table><tr><th>{tr("name")}</th><th>{tr("role")}</th><th>{tr("active")}</th><th></th></tr>{urows}</table></div>
    <div class="card"><form method="post" onsubmit="return confirm('OK?')"><input type="hidden" name="action" value="force_out">
    <button class="btn btn-out" type="submit">{tr("force_out")}</button></form>
    <a class="btn btn-primary" href="{url_for("export_csv")}">{tr("export")}</a></div>'''

@app.route("/export.csv")
@login_required
@require("admin.export")
def export_csv():
    rows=get_db().execute("SELECT e.created_at,u.name,u.role,e.event_type,e.is_late,e.note FROM events e JOIN users u ON u.id=e.user_id ORDER BY e.id").fetchall()
    buf=io.StringIO(); w=csv.writer(buf)
    w.writerow(["time","name","role","event","late","note"])
    for r in rows: w.writerow([r["created_at"],r["name"],r["role"],r["event_type"],r["is_late"],r["note"]])
    return Response(buf.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=campus.csv"})

register_extra(app, {"page": page, "tr": tr, "get_db": get_db, "login_required": login_required,
    "staff_required": staff_required, "admin_required": admin_required,
    "current_status": current_status, "is_late_now": is_late_now})
register_channels(app, {"page": page, "tr": tr, "get_db": get_db, "login_required": login_required})
register_massar(app, {"page": page, "tr": tr, "get_db": get_db, "login_required": login_required})

if __name__=="__main__":
    init_db()
    print("Go to Massar: /massar/go")
    print("http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=True)
