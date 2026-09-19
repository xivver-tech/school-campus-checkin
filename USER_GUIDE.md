# دليل المستخدم / Guide utilisateur
**Rowad Nahda Private — Tiznit** · Campus Check-In

| | |
|--|--|
| **Français** | Guide complet |
| **العربية** | الفصحى |
| **الدارجة** | المغربية |

---

## حدود الصلاحيات · Limites · الحدود

| Role | Français | العربية | الدارجة | Limit |
|------|----------|---------|---------|--------|
| **host** | PC du serveur (pas une personne) | جهاز السيرفر وليس شخصاً | الكمبيوتر اللي فيه السيرفر، ماشي شخص | 1 PC |
| **admin** | Administrateurs | المدراء | الأدمن | **max 3** |
| **appdev** | Développeurs | المطورون | المطورين | **max 2** |

---

## 1. Student · Élève · تلميذ · تلميذ

### Français
Compte **élève**.
- Pointage **entrée / sortie** avec GPS (près de l’école pour entrer)
- Voir **seulement ses canaux de classe**
- Lire les **annonces**
- Ouvrir **Massar** (notes officielles)
- Enregistrer son **Code Massar**
- Voir **son** historique

**Interdit :** panneau admin, créer des canaux, liste globale des absents, changer le GPS.

### العربية
حساب **التلميذ**.
- تسجيل الدخول والخروج عبر GPS
- رؤية **قنوات قسمه فقط**
- قراءة الإعلانات
- فتح **مسار** للنقط الرسمية
- حفظ رقم مسار
- سجل الحضور الشخصي فقط

**ممنوع:** إدارة النظام، إنشاء قنوات، تغيير موقع المدرسة.

### الدارجة
التلميذ كيدير **check-in و check-out** بالـ GPS، كيشوف **غير القنوات ديال القسم ديالو**، كيقرا الإعلانات، كيدخل **Massar** باش يشوف النقط. ما يقدرش يدخل للأدمن ولا يصاوب قنوات.

---

## 2. Teacher · Enseignant · أستاذ · أستاذ

### Français
**Enseignant** — tout ce que fait l’élève, plus :
- **Créer** des canaux de classe (ex. 3A, plusieurs classes)
- **Ajouter** des élèves au canal
- **Publier** devoirs / exercices (visibles seulement par la classe)
- Liste **absents du jour**
- **Pointage manuel**
- **Rapport de la semaine**
- **Tableau campus** (qui est dedans / dehors)
- Publier des **annonces**
- Liste des **Code Massar** des élèves

**Interdit :** gérer tous les comptes admin, changer GPS / horaires.

### العربية
**الأستاذ** — صلاحيات التلميذ مع:
- إنشاء قنوات للأقسام
- إضافة التلاميذ للقناة
- نشر الواجبات والتمارين (للقسم فقط)
- قائمة الغائبين
- تسجيل يدوي
- تقرير الأسبوع
- لوحة من في المدرسة
- الإعلانات وقائمة أرقام مسار

### الدارجة
الأستاذ كيصاوب **قناة لكل قسم**، كيزيد التلاميذ، كينشر الفروض، كيشوف **الغياب**، كيدير pointage يدوي، و التقرير الأسبوعي. ما يقدرش يبدّل GPS ديال المدرسة.

---

## 3. Staff · Personnel · موظف · موظف

### Français
**Personnel** (secrétariat, etc.).
- Pointage GPS
- Absents, pointage manuel, semaine, tableau campus
- Annonces, lien Massar

**Interdit :** créer des canaux de classe, gestion complète des utilisateurs, GPS école.

### العربية
**الموظف** — أدوات الحضور والغياب والتقرير، بدون إدارة كاملة للحسابات.

### الدارجة
الموظف كيستعمل أدوات المدرسة (الغياب، pointage يدوي، التقرير). ما كيسيركاش الحسابات بحال الأدمن.

---

## 4. Bus driver · Chauffeur · سائق الحافلة · سائق الطوبيس

### Français
**Chauffeur de bus**.
- Surtout **entrée / sortie** GPS
- Son historique, annonces, Massar si besoin

**Interdit :** outils prof / admin.

### العربية
**سائق الحافلة** — تسجيل الحضور أساساً.

### الدارجة
سائق الطوبيس كيدير أساساً **الدخول و الخروج** فالتطبيق.

---

## 5. Host · PC serveur · جهاز السيرفر · الكمبيوتر ديال السيرفر

### Français
**Ce n’est PAS une personne.**  
C’est le compte du **ordinateur qui fait tourner le serveur** (bureau, guichet).

Utilisation :
- Compte machine (1 recommandé)
- Afficher éventuellement le **tableau campus** en grand écran
- Le serveur tourne avec `python app.py` même sans login

### العربية
**ليس دور شخص.** هو حساب **جهاز الكمبيوتر الذي يشغّل الخادم** في المدرسة.

### الدارجة
هاد الدور **ماشي ديال بنيادم** — هو حساب **الكمبيوتر اللي فيه السيرفر**. حساب واحد للآلة كافي.

---

## 6. Admin · Administrateur · مدير · أدمن (max 3)

### Français
**Administrateur** — **maximum 3 personnes**.

Peut :
- Tout ce que fait le professeur
- **Ajouter / désactiver** des utilisateurs
- **Export CSV**
- **Forcer la sortie** de tout le monde
- Ouvrir `/admin`

**Ne peut PAS :** changer nom de l’école, GPS, rayon, horaires (verrouillé).  
Seul **appdev** le peut.

Accès admin : menu **Admin** ou `http://IP:5050/admin`

### العربية
**المدير** — **3 أشخاص كحد أقصى**.
- إدارة المستخدمين والتصدير وإجبار الخروج
- **لا يمكنه** تغيير موقع GPS أو أوقات المدرسة

### الدارجة
الأدمن (حتى **3 نفر**) كيزيد المستخدمين و كيدير export. **ما يقدرش** يبدّل GPS أو أوقات المدرسة — غير المطور يقدر.

---

## 7. AppDev · Développeur · مطور · مطور (max 2)

### Français
**Développeur** — **maximum 2 personnes**.
- Tous les droits admin
- **Peut changer** GPS, horaires, nom de l’école
- Réservé à l’équipe technique

### العربية
**المطور** — **شخصان كحد أقصى**. وحده يغيّر إعدادات موقع المدرسة والوقت.

### الدارجة
المطور (حتى **2 نفر**) عندو كلشي + يبدّل **موقع المدرسة و الأوقات**. ما تعطيوش هاد الحساب لأي واحد.

---

## Tableau · جدول الصلاحيات

| Action | student | teacher | staff | bus | host | admin | appdev |
|--------|:-------:|:-------:|:-----:|:---:|:----:|:-----:|:------:|
| Check-in GPS | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Canaux de sa classe | ✓ | ✓ | | | | ✓ | ✓ |
| Créer canaux | | ✓ | | | | ✓ | ✓ |
| Absents / manuel / semaine | | ✓ | ✓ | | ✓ | ✓ | ✓ |
| Ajouter utilisateurs | | | | | | ✓ | ✓ |
| Changer GPS / heures | | | | | | | ✓ |

---

## Connexion · تسجيل الدخول · الدخول

| Français | العربية | الدارجة |
|----------|---------|---------|
| Nom = nom complet du compte | الاسم كما سُجّل | الاسم كامل بحال ما عطاوك |
| PIN = code numérique | الرقم السري | الكود / PIN |
| FR / AR / EN en haut | غيّر اللغة فوق | بدّل اللغة لفوق |

---

## Installation téléphone · الهاتف

### Français
1. Un PC à l’école lance le serveur (`python app.py`)
2. Téléphone sur le **même Wi‑Fi**
3. Ouvrir `http://IP-DU-PC:5050`
4. **Android (Chrome)** : Installer l’application / Ajouter à l’écran d’accueil
5. **iPhone (Safari)** : Partager → Sur l’écran d’accueil
6. Autoriser la **localisation**

### العربية
1. تشغيل السيرفر على كمبيوتر المدرسة
2. الهاتف على نفس الواي فاي
3. فتح الرابط `http://IP:5050`
4. أندرويد: تثبيت / إضافة للشاشة الرئيسية
5. آيفون (سفاري): مشاركة → على الشاشة الرئيسية
6. السماح بالموقع (GPS)

### الدارجة
1. الكمبيوتر ديال المدرسة كيشغّل التطبيق
2. التليفون فنفس الـ Wi‑Fi
3. دخّل الرابط `http://IP:5050`
4. أندرويد: Install / زيد للشاشة
5. آيفون: Share → Add to Home Screen
6. خلّي الـ GPS يخدم

Détail Windows / Linux : voir **README.md**.

---

## Comptes démo · حسابات تجريبية (غيّرها قبل الاستعمال الحقيقي)

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

## Massar · مسار

| Français | العربية | الدارجة |
|----------|---------|---------|
| Bouton **Go to Massar** ouvre le site officiel | زر مسار يفتح الموقع الرسمي | زر Massar كيفتح الموقع الرسمي |
| Notes officielles = Massar | النقط الرسمية = مسار | النقط فـ Massar |
| Cette app = présence GPS + messages de classe | هذا التطبيق = الحضور والرسائل | هاد التطبيق = الحضور و رسائل القسم |

---

*Rowad Nahda Private — Tiznit · Guide FR / عربية / دارجة*
