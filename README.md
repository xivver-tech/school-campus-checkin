# School Campus Check-In System

A **full web app** for tracking who enters and leaves a school campus.

## Concept
- Students / teachers / staff log in with a **name + PIN**
- Big **CHECK IN** button when arriving
- Big **CHECK OUT** button when leaving
- Phone **GPS** is compared to the school location (geofence)
- Must be near the school to check **in**
- Teachers/admin see **who is on campus right now**
- Full history + CSV export

## Features
| Feature | |
|--------|--|
| Roles | admin, teacher, student, staff |
| Geofence | lat/lng + radius (meters) |
| Check-in / out | One-tap buttons |
| Live board | Who’s on campus |
| History | Personal or all (staff) |
| Admin | Add users, set school location, export CSV |
| Storage | SQLite (`campus.db`) |

## Run
```bash
pip install -r requirements.txt
python app.py
```
Open **http://localhost:5050**

### Demo logins
| Name | PIN | Role |
|------|-----|------|
| Admin | 0000 | admin |
| Ms. Rivera | 1234 | teacher |
| Alex Student | 1111 | student |
| Sam Staff | 2222 | staff |

## Setup for a real school
1. Login as **Admin**
2. Open **Admin**
3. Set school name, latitude, longitude, radius (e.g. 150 m)
4. Add real users with PINs

Get coordinates: Google Maps → right-click the school → copy lat/lng.

## How geofence works
Browser asks for location → app computes distance to school center with the Haversine formula → check-in only allowed if within radius (+ GPS accuracy margin).

Works on phones in the browser (HTTPS or localhost required for GPS in most browsers).
