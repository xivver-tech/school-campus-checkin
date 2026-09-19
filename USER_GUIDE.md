# User Guide — Teachers & Admins
**Rowad Nahda Private — Tiznit** · Campus Check-In

Open the app in the browser (phone or computer), then log in with the **name** and **PIN** given by the school.

---

## 1. Login

| Field | What to type |
|--------|----------------|
| **Name** | Full account name (example: `Teacher Demo`) |
| **PIN** | 4+ digit code (example: `1234`) |

- Language: tap **FR** / **AR** / **EN** at the top.
- If login fails: check spelling and spaces in the name.

---

## 2. For teachers

### Home screen
- See your status (**on campus** / **off campus**).
- **Check in / Check out** with GPS (must be near the school).
- Shortcuts: Class channels, Absent, Manual check, Week report, Announcements, **Massar**.

### Class channels (class messages only)
1. Open **Class channels** (or **Channels**).
2. **Create** a channel (example: `3A Maths`).
3. Open the channel → **Add student** (one by one).
4. **Post** homework / after-hours exercises.

**Important:** Students only see channels they were added to — not the whole school.

You can have many channels (several classes).

### Absent today
- Open **Absent**.
- List of students with **no check-in today**.
- Use **Manual check** if someone forgot the phone / GPS.

### Manual check-in
1. Open **Manual check**.
2. Choose the student.
3. Optional reason (medical, transport, family…).
4. Tap **Check in** or **Check out**.

### Week report
- Grid of the week: who was present each day.

### Campus board
- Who is currently **inside** / **outside** the campus.

### Announcements (whole school)
- Open **Announcements**.
- Teachers/staff can **post**; everyone can **read**.

### Massar (official notes)
1. Tap **Go to Massar portal** (or **Massar** in the menu).
2. The **official** Massar website opens.
3. Log in with **Code Massar** + password from the school.
4. Optional: save your Code Massar inside the app so you remember it.
5. **Code Massar list**: see students’ codes (for reference only).

This app does **not** replace Massar.  
- **This app** = GPS presence + class messages.  
- **Massar** = official grades and ministry records.

---

## 3. For admins

Everything teachers can do, **plus**:

### Open the admin panel
- On computer: top menu → **Admin**.
- On phone: go to  
  `http://YOUR-SERVER:5050/admin`  
  (example: `http://192.168.1.111:5050/admin`).

You must be logged in as **Admin** (or **AppDev**).

### Add a user
1. **Admin** → **Add user**.
2. Fill in:
   - **Name** (login name)
   - **PIN**
   - **Role**: student / teacher / staff / busdriver / host / admin  
     (do not create AppDev unless you are the developer)
   - **Class** (optional, e.g. `3A`)
3. Save.
4. Give the person their **name + PIN**.

### Disable a user
- In the users table → **Disable**.  
- They can no longer log in.

### Force everyone out
- **Force out**: marks all current “in” users as out (end of day / emergency).

### Export CSV
- Download attendance history as a spreadsheet file.

### School location & hours (LOCKED)
- Name, GPS, radius, and timetable are **locked** to Rowad Nahda — Tiznit.
- **Admin cannot change them.**
- Only **AppDev** can change GPS/hours (developer).
- This stops another school from reusing the app with different coordinates.

---

## 4. Roles (short)

| Role | Main access |
|------|----------------|
| **student** | Check-in, own class channels, Massar link, announcements |
| **teacher** | + create channels, absent, manual, week, campus |
| **staff / host** | Campus tools (no full admin) |
| **busdriver** | Check-in mainly |
| **admin** | Users, export, force out (+ teacher tools) |
| **appdev** | Everything including school GPS/hours |

---

## 5. Daily routines (suggested)

### Morning (teacher / staff)
1. Students **check in** on arrival (GPS).
2. After ~15–20 min: open **Absent** → call / follow up.
3. Use **Manual check** for justified late arrivals.

### During the day
- Post homework in the **class channel** (not the whole-school feed).
- Use **Announcements** only for school-wide news.

### Evening
- Students **check out** when leaving.
- Optional: **Force out** if someone forgot.
- Optional: **Export CSV** for archives.

### Grades
- Always enter official notes in **Massar** (button in the app).

---

## 6. Common problems

| Problem | What to do |
|---------|------------|
| “Too far” on check-in | Must be near the school (GPS). Outside campus = blocked for IN. |
| No GPS | Allow location in the browser; use HTTPS or phone; try **Refresh GPS**. |
| Student doesn’t see channel | Teacher must **Add student** to that channel. |
| Can’t open Admin | Only Admin/AppDev. On phone use `/admin` URL. |
| Massar button | Opens the official site — use school Code Massar + password. |
| Forgot PIN | Admin creates a new user or resets via a new account (no self-reset yet). |

---

## 7. Demo accounts (testing only)

| Name | PIN | Role |
|------|-----|------|
| Admin | 0000 | admin |
| Teacher Demo | 1234 | teacher |
| Student Demo | 1111 | student |
| Staff Demo | 2222 | staff |
| AppDev | 9999 | appdev |

**Change these PINs before real use at school.**

---

## 8. Privacy note

- Attendance and location events are stored for the school.
- Code Massar is stored only if the user saves it.
- Massar passwords are **never** stored in this app.

---

*Guide version for Campus Check-In · Rowad Nahda Private — Tiznit*
