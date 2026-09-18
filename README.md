# Rowad Nahda Private — Tiznit · Campus Check-In

FR / AR / EN · phone-ready · GPS geofence

## Run
```bash
pip install -r requirements.txt
python app.py
```
(`app.py` loads `app_full.py` + `extra.py` + `i18n.py`)

## Languages
Header: **FR** · **AR** · **EN** (Arabic is RTL)

## Features
| Feature | Who | Path |
|--------|-----|------|
| GPS Check-in / out | Everyone | Home |
| Late detection | Auto | — |
| Who is on campus | Staff | /campus |
| Daily report | Staff | /report |
| **Absent today** | Staff | /absent |
| **Manual pointage** | Staff | /manual |
| **Week grid** | Staff | /week |
| **Announcements** | All (post: staff) | /announce |
| Class groups | Admin | Admin → Add user |
| Force checkout | Admin | Admin |
| CSV export | Admin | Admin |

## Demo logins
Admin/`0000` · Teacher Demo/`1234` · Student Demo/`1111` · Staff Demo/`2222`

## School config (Admin)
Name, lat/lng (gate), radius, hours 08:00–16:00, late after 08:15  
GPS default = Tiznit center — change to exact school gate.
