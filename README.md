# Rowad Nahda Private — Tiznit · Campus Check-In

GPS check-in · class channels · Massar link · FR / AR / EN  
**Web app** — runs on a school PC, used from phones as an installable app (PWA).

Full role guide: **[USER_GUIDE.md](USER_GUIDE.md)**

---

## Roles (policy)

| Role | Meaning | Limit |
|------|---------|--------|
| **student** | Élève | many |
| **teacher** | أستاذ | many |
| **staff** | Personnel | many |
| **busdriver** | سائق الحافلة | many |
| **host** | **Not a person** — account for the **PC that runs the server** | 1 recommended |
| **admin** | School admin | **max 3 people** |
| **appdev** | Developer | **max 2 people** |

Only **appdev** can change school GPS / hours (locked to Rowad Nahda).

---

## 1. Install the SERVER (one computer at school)

This PC stays on and runs the app. Everyone else connects with phone or browser.

### Requirements
- **Python 3.10+**
- Network (Wi‑Fi) so phones can reach this PC

### Linux (Ubuntu / Debian / etc.)

```bash
sudo apt update
sudo apt install -y python3 python3-pip git

git clone https://github.com/xivver-tech/school-campus-checkin.git
cd school-campus-checkin

python3 -m pip install -r requirements.txt
python3 app.py
```

Open: `http://127.0.0.1:5050`  
On the LAN: `http://IP-OF-THIS-PC:5050` (example `http://192.168.1.111:5050`)

Leave the terminal open. Stop with `Ctrl+C`.

### Windows

1. Install Python from https://www.python.org/downloads/  
   → check **Add Python to PATH**
2. Install Git (optional) from https://git-scm.com/  
   Or download **ZIP** from GitHub → Extract
3. Open **Command Prompt** or PowerShell:

```bat
cd school-campus-checkin
python -m pip install -r requirements.txt
python app.py
```

4. Browser: http://127.0.0.1:5050  
5. Find PC IP: `ipconfig` → use `http://THAT-IP:5050` on phones

### Firewall
Allow port **5050** on the server PC so phones on Wi‑Fi can connect.

---

## 2. Use on Android (install as app)

The app is a **website** you can “install” on the phone (PWA-style).

1. Connect phone to the **same Wi‑Fi** as the server PC
2. Chrome → open `http://IP-OF-SERVER:5050`  
   (example: `http://192.168.1.111:5050`)
3. Menu **⋮** → **Install app** / **Add to Home screen** / **Install page**
4. Icon appears on home screen → opens full screen like an app
5. Allow **Location** when asked (for check-in)

If “Install” does not appear: **Add to Home screen** still works.

---

## 3. Use on iPhone / iPad

1. Same Wi‑Fi as the server
2. **Safari** (required for Add to Home Screen) → `http://IP-OF-SERVER:5050`
3. Share button **□↑** → **Add to Home Screen**
4. Name it e.g. `Campus` → Add
5. Open from home screen
6. Allow **Location** for check-in

Note: GPS on iPhone works best when opened from the home-screen icon.

---

## 4. Use on Windows / Linux (staff browser)

No extra install for users:

1. Chrome / Firefox / Edge
2. Go to `http://IP-OF-SERVER:5050`
3. Optional: browser menu → **Install** / pin tab
4. Login with name + PIN

---

## 5. First login (demo — change PINs for real school)

| Name | PIN | Role |
|------|-----|------|
| Admin | 0000 | admin |
| Teacher Demo | 1234 | teacher |
| Student Demo | 1111 | student |
| Staff Demo | 2222 | staff |
| Bus Demo | 3333 | busdriver |
| Host Demo | 4444 | host (server PC) |
| AppDev | 9999 | appdev |

Admin panel: http://IP:5050/admin  
User guide: [USER_GUIDE.md](USER_GUIDE.md)

---

## 6. Features (short)

- GPS check-in / out (geofence locked to school)
- Class channels (students see only their class)
- Absent list, manual pointage, week report, campus board
- Announcements
- Massar button → official portal
- FR / AR / EN

---

## 7. Production tips

- Keep the **server PC** on during school hours
- Use a fixed local IP for the server if possible
- Change all demo PINs
- Max **3 admins**, max **2 appdev**
- **host** = machine account, not a person
- For internet access outside Wi‑Fi you need a public host + HTTPS (advanced)

---

```bash
git clone https://github.com/xivver-tech/school-campus-checkin.git
cd school-campus-checkin
python -m pip install -r requirements.txt
python app.py
```
