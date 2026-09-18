# Rowad Nahda Private — Tiznit · Campus Check-In

GPS check-in · FR/AR/EN · **class channels** · multi-role

## Class channels (main new feature)
- A **teacher** can create many class channels (e.g. 8 classes, 900+ students total).
- **Students only see channels they are members of** — not the whole school feed.
- Teacher posts homework / after-hours exercises **only to that class**.
- Path: **/channels**

### How to use
1. Login as **Teacher Demo** / `1234`
2. Open **Class channels** → create e.g. `3A Maths`
3. Open the channel → **Add student** (Student Demo)
4. Login as **Student Demo** / `1111` → **Channels** → only sees `3A Maths`
5. Teacher posts messages; students read them in their class only

## Roles (Admin can assign)
| Role | Access |
|------|--------|
| **student** | Check-in, own class channels |
| **teacher** | Channels they own, campus tools |
| **staff** | Campus tools |
| **busdriver** | Check-in (bus) |
| **host** | Campus tools |
| **admin** | Everything |
| **appdev** | Admin-level |

## Run
```bash
pip install -r requirements.txt
python app.py
```

## Demo accounts
| Name | PIN | Role |
|------|-----|------|
| Admin | 0000 | admin |
| Teacher Demo | 1234 | teacher |
| Student Demo | 1111 | student |
| Staff Demo | 2222 | staff |
| Bus Demo | 3333 | busdriver |
| Host Demo | 4444 | host |

Files: `app.py` → `app_full.py` + `channels.py` + `extra.py` + `i18n.py`
