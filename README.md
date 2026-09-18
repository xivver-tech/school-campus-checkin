# Rowad Nahda Private — Tiznit · Campus Check-In

Base app for **Rowad Nahda Private School (Tiznit, Morocco)**.

## Pre-configured
| Setting | Value |
|--------|--------|
| School | Rowad Nahda Private — Tiznit |
| GPS (city center) | 29.6974, -9.7316 |
| Radius | 200 m (change to exact gate later) |
| Hours | 08:00 – 16:00 |
| Late after | 08:15 |
| Timezone | Africa/Casablanca (device local time) |

## Run
```bash
pip install -r requirements.txt
python app.py
```
- PC: http://localhost:5050  
- Phone (same Wi‑Fi): http://YOUR-PC-IP:5050 → **Add to Home Screen**

## Demo logins
| Name | PIN | Role |
|------|-----|------|
| Admin | 0000 | admin |
| Teacher Demo | 1234 | teacher |
| Student Demo | 1111 | student |
| Staff Demo | 2222 | staff |

## Before real use
1. Login as **Admin**
2. Set **exact school gate** lat/lng (Google Maps → right‑click)
3. Adjust radius if needed (e.g. 80–150 m)
4. Add real teachers/students with PINs

If you like this base, we can continue (Arabic UI, more users, reports, etc.).
