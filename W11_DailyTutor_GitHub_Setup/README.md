# 🪟 W11 Daily Tutor – Vollautomatischer Anleitungs-Generator

Jeden Morgen um **06:00 Uhr** generiert dieser GitHub Action automatisch **2 neue Windows 11 Anleitungen** im Stil der Fachschaft Digitalität – ohne dass du den Laptop öffnen musst.

---

## 📁 Ordnerstruktur

```
w11-daily-tutor/
├── .github/
│   └── workflows/
│       └── w11_daily_tutor.yml   ← Automatischer Zeitplan
├── scripts/
│   ├── gen_daily.py              ← Hauptskript (Claude API + Word)
│   └── used_topics.json          ← Themen-Tracking (7 Tage)
├── template/
│   └── Vorlage_Fachschaft_Digitalitaet.dotx   ← Deine Word-Vorlage
├── output/
│   └── 02-05-2026/
│       ├── W11_02.05.2026_Anleitung1_...docx
│       └── W11_02.05.2026_Anleitung2_...docx
└── README.md
```

---

## ⚙️ Einmalig einrichten (15 Minuten)

### Schritt 1 – GitHub Repository erstellen

1. Gehe zu [github.com](https://github.com) → **New repository**
2. Name: `w11-daily-tutor`
3. **Private** auswählen (deine Anleitungen bleiben privat)
4. Klicke **Create repository**

### Schritt 2 – Dateien hochladen

**Option A – GitHub Web (einfacher):**
1. Klicke auf **uploading an existing file**
2. Ziehe den kompletten Inhalt dieses ZIP-Ordners hinein
3. Klicke **Commit changes**

**Option B – Git Terminal:**
```bash
git clone https://github.com/DEIN-USERNAME/w11-daily-tutor.git
# Alle Dateien in den Ordner kopieren
cd w11-daily-tutor
git add .
git commit -m "🚀 W11 Daily Tutor einrichten"
git push
```

### Schritt 3 – Claude API Key hinterlegen

1. Gehe zu [console.anthropic.com](https://console.anthropic.com)
2. **API Keys** → **Create Key** → kopieren
3. In GitHub: **Settings** → **Secrets and variables** → **Actions**
4. Klicke **New repository secret**
   - Name: `ANTHROPIC_API_KEY`
   - Value: Deinen API Key einfügen
5. **Add secret** klicken

### Schritt 4 – Ersten Test starten

1. In GitHub: **Actions** → **W11 Daily Tutor**
2. Klicke **Run workflow** → **Run workflow**
3. Warte ~60 Sekunden
4. Im **output/**-Ordner erscheinen deine ersten 2 Anleitungen! 🎉

---

## 📅 Wochenplan

| Tag | Anleitung 1 | Anleitung 2 |
|-----|------------|------------|
| Montag | W11 Basics | OneDrive |
| Dienstag | Office 365 | Teams |
| Mittwoch | W11 Basics | Edge |
| Donnerstag | Teams | OneDrive |
| Freitag | Office 365 | W11 |
| Samstag | Edge | Teams |
| Sonntag | W11 Basics | OneDrive |

> Kein Thema wird in 7 Tagen wiederholt.

---

## 📂 Wo findest du die Dateien?

### Option A – Direkt in GitHub
- Gehe zu deinem Repository
- Ordner **output/** → **Datum** → .docx herunterladen

### Option B – OneDrive Sync (empfohlen ⭐)
Synchronisiere den `output/`-Ordner mit OneDrive:

```bash
# Einmalig: Repository direkt in deinen OneDrive-Ordner klonen
git clone https://github.com/DEIN-USERNAME/w11-daily-tutor.git "C:\Users\DEIN-NAME\OneDrive\W11 Daily Tutor"
```

Dann täglich: GitHub Desktop öffnen → **Fetch origin** → neue Dateien erscheinen automatisch in OneDrive.

---

## 💰 Kosten

| Dienst | Kosten |
|--------|--------|
| GitHub (Private Repo) | **Gratis** |
| GitHub Actions (2000 Min/Monat) | **Gratis** |
| Claude API (claude-opus-4-5) | ~$0.05–0.10 pro Tag |

→ **Ca. $1.50–3.00 pro Monat** für täglich 2 Anleitungen.

---

## 🔧 Anpassen

**Uhrzeit ändern** (in `.github/workflows/w11_daily_tutor.yml`):
```yaml
- cron: "0 5 * * *"   # = 06:00 Uhr Schweizer Zeit
# Beispiele:
# "0 4 * * *"  = 05:00 Uhr
# "0 7 * * *"  = 08:00 Uhr
```

**Nur Werktage:**
```yaml
- cron: "0 5 * * 1-5"   # Montag–Freitag
```

---

## ❓ Häufige Fragen

**F: Die Aktion schlägt fehl – was tun?**
A: Actions → Klick auf den fehlgeschlagenen Run → Logs lesen. Häufigste Ursache: API Key fehlt oder ist falsch.

**F: Kann ich die Vorlage aktualisieren?**
A: Ja! Ersetze einfach `template/Vorlage_Fachschaft_Digitalitaet.dotx` durch deine neue Version und committe.

**F: Wie viele Anleitungen werden gespeichert?**
A: Alle – für immer. Jeder Tag bekommt seinen eigenen Unterordner in `output/`.
