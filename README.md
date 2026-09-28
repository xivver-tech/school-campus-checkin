# Rowad Nahda Private — Tiznit · Campus Check-In

GPS check-in · class channels · Massar · **FR / العربية / الدارجة**

**Guide complet (tous les rôles) :** [USER_GUIDE.md](USER_GUIDE.md)  
→ Français + العربية الفصحى + الدارجة المغربية

**Présentation école (FR, terminée) :** [Presentation_Pointage_Campus_FR.pptx](Presentation_Pointage_Campus_FR.pptx)  
→ 16 diapositives : problème, solution, fonctionnalités, rôles, GPS, Massar, accès, comptes démo, feuille de route

Voir aussi [PRESENTATION.md](PRESENTATION.md)

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
sudo apt install -y python3 python3-pip python3-venv git
git clone https://github.com/xivver-tech/school-campus-checkin.git
cd school-campus-checkin
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
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
AppDev (contrôle total, GPS / horaires 8–12 et 14–18) : PIN **9999**

---

## Horaires école

| Séance | Heures | Retard après |
|--------|--------|--------------|
| Matin | 08:00 – 12:00 | 08:15 |
| Après-midi | 14:00 – 18:00 | 14:15 |
