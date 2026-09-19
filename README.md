# Rowad Nahda Private — Tiznit · Campus Check-In

GPS check-in · class channels · Massar · **FR / العربية / الدارجة**

**Guide complet (tous les rôles) :** [USER_GUIDE.md](USER_GUIDE.md)  
→ Français + العربية الفصحى + الدارجة المغربية

---

## Rôles / الأدوار / الأدوار

| Role | FR | عربية | دارجة | Limit |
|------|----|-------|-------|--------|
| student | Élève | تلميذ | تلميذ | — |
| teacher | Enseignant | أستاذ | أستاذ | — |
| staff | Personnel | موظف | موظف | — |
| busdriver | Chauffeur | سائق الحافلة | سائق الطوبيس | — |
| **host** | **PC serveur (pas une personne)** | جهاز السيرفر | الكمبيوتر ديال السيرفر | 1 PC |
| **admin** | Administrateur | مدير | أدمن | **max 3** |
| **appdev** | Développeur | مطور | مطور | **max 2** |

---

## Installer le SERVEUR (1 PC)

### Linux
```bash
sudo apt install -y python3 python3-pip git
git clone https://github.com/xivver-tech/school-campus-checkin.git
cd school-campus-checkin
python3 -m pip install -r requirements.txt
python3 app.py
```

### Windows
1. Installer Python (cochez **Add to PATH**) : https://www.python.org/downloads/
2. Ouvrir CMD dans le dossier du projet :
```bat
python -m pip install -r requirements.txt
python app.py
```
3. Navigateur : http://127.0.0.1:5050  
4. IP du PC (`ipconfig`) pour les téléphones : `http://IP:5050`

---

## Téléphone = “application”

Même Wi‑Fi que le PC serveur → ouvrir `http://IP-DU-PC:5050`

| | |
|--|--|
| **Android (Chrome)** | ⋮ → Installer l’appli / Ajouter à l’écran d’accueil |
| **iPhone (Safari)** | Partager □↑ → Sur l’écran d’accueil |
| **Autoriser GPS** | Obligatoire pour le pointage |

### العربية
الهاتف على نفس الواي فاي → الرابط `http://IP:5050` → إضافة للشاشة الرئيسية → السماح بالموقع.

### الدارجة
التليفون فنفس الـ Wi‑Fi → دخّل الرابط → زيد للشاشة الرئيسية → خلّي الـ GPS.

---

## Comptes démo (à changer en production)

| Name | PIN | Role |
|------|-----|------|
| Admin | 0000 | admin |
| Teacher Demo | 1234 | teacher |
| Student Demo | 1111 | student |
| Staff Demo | 2222 | staff |
| Bus Demo | 3333 | busdriver |
| Host Demo | 4444 | host (PC) |
| AppDev | 9999 | appdev |

Admin : http://IP:5050/admin

---

```bash
git clone https://github.com/xivver-tech/school-campus-checkin.git
cd school-campus-checkin
python -m pip install -r requirements.txt
python app.py
```
