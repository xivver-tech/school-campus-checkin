# User Guide — All Roles
**Rowad Nahda Private — Tiznit** · Campus Check-In

FR · Darija notes included where useful.

---

## Important limits

| Role | Who | Limit |
|------|-----|--------|
| **host** | Not a person — the **PC that runs the server** (kiosk / office computer) | 1 machine account recommended |
| **admin** | Real administrators | **Max 3 people** |
| **appdev** | App developers only | **Max 2 people** |

---

## 1. Student · تلميذ

**Français**  
Compte élève.

**What you can do**
- Check **IN** / **OUT** with GPS (near school only for IN)
- See **only your class channels** (not all school)
- Read school **announcements**
- Open **Massar** (official notes website)
- Save your **Code Massar** in the app
- See your own **history**

**Darija**  
كيدير الدخول/الخروج بالـ GPS، كيشوف غير قنوات القسم ديالو، كيقرا الإعلانات، كيدخل Massar للنقط.

**You cannot:** admin panel, create channels, see all absents, change school settings.

---

## 2. Teacher · أستاذ

**Français**  
Enseignant.

**What you can do**
- Everything a student can (check-in, Massar, etc.)
- **Create class channels** (e.g. 3A, 4B — many classes OK)
- **Add students** to each channel
- **Post** homework / exercises (only that class sees it)
- **Absent today** list
- **Manual check-in** for a student
- **Week report**
- **Campus board** (who is in/out)
- Post **announcements**
- See **Code Massar list** of students

**Darija**  
كيصاوب قنوات الأقسام، كيزيد التلاميذ، كينشر الفروض، كيشوف الغياب و التقرير.

**You cannot:** add/remove admin accounts, change school GPS/hours.

---

## 3. Staff · موظف

**Français**  
Personnel de l’école (secrétariat, etc.).

**What you can do**
- Check-in / out
- Campus board, absent, manual check, week report
- Announcements
- Massar link
- Read class channels if added as member (usually not needed)

**You cannot:** create class channels, manage all users, change GPS.

---

## 4. Bus driver · سائق الحافلة

**Français**  
Chauffeur.

**What you can do**
- **Check IN / OUT** (main use)
- Own history
- Massar link if needed
- Read announcements

**You cannot:** campus tools, channels admin, user management.

**Darija**  
أساساً كيسجّل الدخول و الخروج فالتطبيق.

---

## 5. Host · جهاز السيرفر (not a person)

**Français**  
**Ce n’est pas un rôle pour une personne.**  
C’est le compte du **PC fixe** qui fait tourner le serveur (bureau, guichet, salle des profs).

**Use**
- Leave this account logged in on the **server computer** if you want a shared screen
- Or simply don’t use login on that PC — the server runs in the terminal either way
- Optional: open **Campus board** full screen for the guard desk

**Darija**  
هاد الدور **ماشي ديال شخص** — هو حساب **الكمبيوتر اللي فيه السيرفر**.

**Recommended:** 1 host account for the machine, PIN known only by IT/admin.

---

## 6. Admin · مدير (max 3 people)

**Français**  
Administrateur scolaire. **Maximum 3 personnes.**

**What you can do**
- Everything teachers can do
- **Add / disable users**
- **Export CSV** (attendance file)
- **Force out** everyone
- Open **Admin panel** (`/admin`)

**What you cannot do**
- Change **school name, GPS, radius, hours** (LOCKED for Rowad Nahda)
- Only **AppDev** can unlock those

**How to open Admin panel**
- Computer: menu **Admin**
- Phone: `http://SERVER-IP:5050/admin`

**Darija**  
كيزيد المستخدمين، كيوصلّح الحسابات، كيدير export. **ما يقدرش** يبدّل GPS ديال المدرسة.

---

## 7. AppDev · مطور (max 2 people)

**Français**  
Développeur technique. **Maximum 2 personnes.**

**What you can do**
- Everything admin can do
- **Change school GPS, radius, name, timetable** (only this role)
- Full technical control

**Darija**  
غير المطور يقدر يبدّل موقع المدرسة و الأوقات فالتطبيق.

Keep PINs secret. Do not give AppDev to normal staff.

---

## Quick comparison

| Action | student | teacher | staff | bus | host (PC) | admin (≤3) | appdev (≤2) |
|--------|:-------:|:-------:|:-----:|:---:|:---------:|:----------:|:-----------:|
| GPS check-in | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Own class channels | ✓ | ✓ | | | | ✓ | ✓ |
| Create channels | | ✓ | | | | ✓ | ✓ |
| Absent / manual / week | | ✓ | ✓ | | ✓* | ✓ | ✓ |
| Campus board | | ✓ | ✓ | | ✓* | ✓ | ✓ |
| Add users | | | | | | ✓ | ✓ |
| Change GPS / hours | | | | | | | ✓ |

\* Host PC account can open these if you use it as a desk display.

---

## Daily tips

**Teachers**  
Morning → check Absents → Manual for justified late → post homework in **class channel** only.

**Admins**  
Create accounts at year start → disable leavers → export CSV weekly if needed.

**Everyone**  
Official grades stay on **Massar** (button in the app).

---

## Demo logins (change before real school use)

| Name | PIN | Role |
|------|-----|------|
| Admin | 0000 | admin |
| Teacher Demo | 1234 | teacher |
| Student Demo | 1111 | student |
| Staff Demo | 2222 | staff |
| Bus Demo | 3333 | busdriver |
| Host Demo | 4444 | host (PC) |
| AppDev | 9999 | appdev |

---

See **README.md** for install on Windows, Linux, Android, iPhone.
