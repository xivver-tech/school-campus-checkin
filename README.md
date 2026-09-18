# School Campus Check-In (Phone-ready)

Full school entry/exit system — optimized for **phones** as a installable web app.

## Phone setup
1. Run the server on a computer on the same Wi‑Fi:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
2. On your phone open `http://YOUR-COMPUTER-IP:5050`
3. Browser menu → **Add to Home Screen** (PWA)
4. Allow **location** when checking in

GPS needs localhost or HTTPS in most browsers. On a local network, many phones still allow GPS for local IPs.

## New / expanded features
| Feature | Details |
|--------|--------|
| **Mobile UI** | Large buttons, bottom nav, safe-area padding |
| **PWA** | Manifest + icon + “Add to Home Screen” |
| **Live GPS** | Continuous watch + refresh button |
| **Notes** | Optional note on each check-in/out |
| **Late detection** | Marks LATE if check-in after configured time |
| **School hours** | Start / end / late-after in Admin |
| **Campus board** | Who’s in/out + auto-refresh every 30s |
| **Daily report** | Today’s check-ins + late count |
| **Force checkout** | End-of-day mass checkout (admin) |
| **CSV export** | Full event log |

## Demo logins
| Name | PIN | Role |
|------|-----|------|
| Admin | 0000 | admin |
| Ms. Rivera | 1234 | teacher |
| Alex Student | 1111 | student |
| Sam Staff | 2222 | staff |

## Admin setup for a real school
1. Login as Admin → **Admin**
2. Set school name, lat, lng, radius (meters)
3. Set start / end / late-after times
4. Add users with PINs

Coordinates: Google Maps → right-click school → copy lat,lng.

Repo: https://github.com/xivver-tech/school-campus-checkin
