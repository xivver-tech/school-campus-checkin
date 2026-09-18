# RBAC + Institution Lock

## School lock (anti-clone)
**GPS coordinates, radius, school name, and hours are LOCKED** to:

- **Rowad Nahda Private - Tiznit**
- Lat `29.6974` · Lng `-9.7316` · Radius `200 m`
- Hours `08:00–16:00` · Late after `08:15`

| Who | Can change location / hours? |
|-----|------------------------------|
| student, teacher, staff, busdriver, host | No |
| **admin** | No (fields read-only) |
| **appdev** | **Yes** only |

Files: `school_lock.py` · permission `admin.school_lock`

Geofence check-in always uses the locked coordinates — even if someone edits the DB.

## Demo AppDev
- Name: `AppDev` · PIN: `9999` · role: `appdev`

## Roles & permissions
See `rbac.py`. Admin can manage users/export/force-out but **cannot** re-point the app to another school.
