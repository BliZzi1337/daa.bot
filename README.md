# 🛠️ DAA Discord Bot

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

Ein modular entwickelter Discord-Bot speziell für Fachinformatiker-Umschulungen und IT-Communities.  
Bietet eine Vielzahl an Automatisierungen, Tools und Admin-Features – von interaktiven Quizzen über Systemtools bis zur Voice-Channel-Steuerung.

🌐 **Webinterface:** [bot.blizzi1337.de](https://bot.blizzi1337.de)

---

## ⚙️ Hauptfunktionen

| Feature                | Beschreibung |
|------------------------|--------------|
| 🌐 **Webinterface**     | Live-Status, Voice-Tracking und Quiz-Statistiken via [bot.blizzi1337.de](https://bot.blizzi1337.de) |
| 🔢 `/bytes`             | Speichergrößen-Rechner inkl. Formeln und Rechenweg |
| 🔣 `/convert`           | Binär-, Dezimal- und Hex-Umwandlungen mit Erklärungen |
| ⚡ `/usv`               | USV-Kalkulation mit Eingabemasken & Formelunterstützung |
| 🔁 `/verschieben`       | Admin-Command zum Channelwechsel aller Mitglieder |
| 🎡 `/rad`             | Zufallsrad zur Entscheidungsfindung |
| 🧠 `/quiz`              | Interaktives Lernfeld-Quiz mit UI (Dropdowns & Buttons) |
| 🛠️ `!move`              | Manuelles Verschieben mit Admin-Check |
| ⏰ **Auto-Move**         | Automatische Voice-Verschiebung (Di–Fr, 11:15 Uhr) |
| ♻️ **Voice-System**      | Automatisches Erstellen/Löschen von Voice-Talks |
| 🧹 **Channel-Reorg**     | Stets nur ein leerer Voice-Talk – ohne Duplikate |
| 📜 **Join-Logs**         | Logging aller Channel-Beitritte, -Wechsel & -Verlassen |
| 📊 **Statistik-Button** | Lernfortschritt in % (richtig/gesamt) pro Lernfeld |
| 🧾 **Fortschritt**       | Automatische Bewertung, Punktevergabe & Speicherung |

---

## 📁 Projektstruktur

```bash
discord_bot/
├── main.py                     # Einstiegspunkt, Cog-Loader & Status-Handling
├── cogs/                       # Slash- & Textcommands (modular aufgebaut)
│   ├── convert_cog.py          # `/convert`: Zahlensystem-Rechner
│   ├── bytes_cog.py            # `/bytes`: Speichergrößen-Konverter
│   ├── usv_cog.py              # `/usv`: USV-Rechner mit Formeln
│   ├── move_anywhere_cog.py    # `/verschieben`: Admin-Channelmove
│   ├── reload_cog.py           # `/reload`: Cogs neuladen (nur Owner)
│   ├── wheel_cog.py            # Zufallsrad-Logik
│   └── quiz_cog.py             # `/quiz`: Lernfeld-Fragen & UI
└── modules/                    # Hintergrundprozesse & Listener
    ├── move.py                 # Auto-Move-Logik & `!move` Command
    ├── auto_voice.py           # Dynamisches Voice-Management
    ├── websocket_handler.py    # WebSocket-Schnittstelle
    └── quiz_manager.py         # Quiz-Fragen-Logik & Fortschrittsspeicherung
```

---

## 🔧 Einrichtung

1. `.env` Datei mit allen erforderlichen Token/IDs anlegen
2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
3. Bot starten:
   ```bash
   python main.py
   ```

---

## 🔐 Discord-Berechtigungen

- Nachrichten lesen & schreiben  
- Sprachkanal-Mitglieder verschieben  
- Voice Intents aktivieren  
- Slash-Commands verwalten  

---

## 👨‍💻 Entwickler

**Chris** aka `BliZzi1337`  
Discord-Admin, Entwickler & Lernunterstützer mit ❤️ für Automatisierung & moderne Tools.  
Aktiv in der Fachinformatiker-Community.

---

## 📜 Lizenz

MIT-Lizenz.  
Private Nutzung erlaubt – Veröffentlichung oder Weiterverbreitung bitte nur mit Genehmigung.
