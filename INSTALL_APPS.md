# Installing the campus app (phones & computers)

This project is a **web app**. One server runs it; phones and PCs open it in a browser.
That is normal for school tools and is what we use for the demo.

---

## What you get today (recommended)

| Device | How users open it |
|--------|-------------------|
| **Android** | Chrome → open the school link → **Add to Home screen** / Install |
| **iPhone / iPad** | **Safari only** → Share → **Add to Home Screen** |
| **Windows / Linux PC** | Browser bookmark, or install from the browser menu |

After that it looks like an app icon. GPS works best over **HTTPS** (Render gives HTTPS).

**iOS:** there is no free side-loaded “IPA” like an APK. Apple only allows App Store apps or this Safari home-screen method unless you pay for a developer account and build a native shell.

---

## Real APK / EXE / Flatpak — honest status

| Package | Possible? | What it really is |
|---------|-----------|-------------------|
| **APK (Android)** | Yes, later | A small shell (Capacitor / TWA) that opens your hosted site |
| **EXE (Windows)** | Yes, later | Usually Electron or a shortcut to the website; or PyInstaller for the *server* only |
| **Flatpak (Linux)** | Possible, rare for schools | Linux package of the same web/desktop shell |
| **iOS App Store** | Paid Apple account + review | Not free; Safari home screen is the free path |

We do **not** ship a finished Play Store APK or App Store build in this repo yet.
The product works as a website first; native packages can wrap the same URL when the school pays for hosting + domain.

---

## Practical plan for Rowad Nahda

### Phase 1 — Demo (now)
1. Host on Render (free link) or school PC on Wi‑Fi
2. Teachers/students: browser → Add to Home Screen
iPhone: Safari only

### Phase 2 — School says yes
1. Domain `rowadnahda.ma`
2. Always-on host
3. Same app, cleaner address

### Phase 3 — Optional native packages
1. **Android APK:** Capacitor or Trusted Web Activity pointed at `https://rowadnahda.ma`
2. **Windows:** desktop shortcut or a tiny Electron wrapper
3. **Linux Flatpak:** only if the IT team asks for it
4. **iOS:** keep Safari home screen, or Apple Developer program later

---

## Why not “just make APK + EXE + Flatpak” in one go?

- Each platform needs different tooling (Android SDK, Windows signing, Flatpak runtime).
- An APK that only embeds the site still needs your **server online**.
- Fake offline-only APKs would not share one live attendance database.

So: **one live server + installable web icons** is the correct architecture for this school system.

---

## Front page languages

In the app UI: **French, Arabic (standard), English** only.

Darija explanations stay in the **full written guide** (`USER_GUIDE.md`), not on the login screen.
