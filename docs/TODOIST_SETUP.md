# Todoist Setup Guide

## 📋 Übersicht

MMM-UniAssignments synchronisiert sich mit einem Todoist-Projekt und zeigt Uni-Abgaben im MagicMirror an.

## 🔑 API Token

### Token besorgen

1. Öffne [Todoist Settings > Integrations](https://todoist.com/prefs/integrations)
2. Scrolle zu "API token"
3. Kopiere deinen Token
4. Füge ihn in `backend/.env` ein:

```env
TODOIST_API_TOKEN=dein_token_hier
```

⚠️ **Wichtig**: Token niemals in Git committen!

---

## 📁 Projekt-Struktur

### Projekt erstellen

1. Erstelle ein Todoist-Projekt namens **"UNI"**
2. Füge Sections für deine Module hinzu (z.B. "Mathematik", "Informatik")

### Beispiel-Struktur

```
📚 UNI (Projekt)
├── 📘 Mathematik (Section)
│   ├── ✓ Übungsblatt 1 #abgabe
│   ├── ⬜ Übungsblatt 2 #abgabe
│   └── ⬜ Probeklausur #abgabe
│
├── 💻 Informatik (Section)
│   ├── ✓ Projekt Proposal #abgabe
│   └── ⬜ Abschlusspräsentation #abgabe
│
└── 🧪 Physik (Section)
    └── ⬜ Laborprotokoll #abgabe
```

---

## 🏷️ Labels

### Assignment Label

Alle Aufgaben, die im Mirror angezeigt werden sollen, müssen das Label `abgabe` haben.

**Label erstellen:**
1. Öffne Todoist Einstellungen
2. Gehe zu "Labels"
3. Erstelle Label "abgabe"

**Label zuweisen:**
- Bei Task-Erstellung: `#abgabe` eingeben
- Bei bestehendem Task: Rechtsklick → Labels → abgabe

---

## 📅 Fälligkeitsdaten

### Format

Todoist unterstützt verschiedene Datumsformate:

```
Morgen
Montag
15. Januar
15.01.2024
in 3 Tagen
```

### Best Practices

✅ **Empfohlen:**
- Nutze spezifische Daten (15.01.2024)
- Setze Uhrzeiten für Abgaben (15.01.2024 23:59)

❌ **Vermeiden:**
- Wiederkehrende Abgaben (außer sinnvoll)
- Keine Daten bei Abgaben

---

## 🔄 Synchronisation

### Automatisch

Das Backend synchronisiert automatisch:
- **Beim Start**: Initial-Sync
- **Alle 5 Minuten**: Im MagicMirror-Modul

### Manuell

```bash
# Via API
curl -X POST http://localhost:5000/api/sync

# Via Python
cd MMM-UniAssignments/backend
source venv/bin/activate
python3 todoist_sync.py
```

---

## 📊 Datenstruktur

### Was wird synchronisiert?

**Pro Abgabe:**
- ✅ Titel
- ✅ Beschreibung
- ✅ Fälligkeitsdatum
- ✅ Modul (Section)
- ✅ Priorität
- ✅ Erledigungs-Status
- ✅ Labels

**Nicht synchronisiert:**
- ❌ Kommentare
- ❌ Sub-Tasks
- ❌ Anhänge

### Cache

Daten werden in `backend/assignments.json` gecacht:

```json
{
  "assignments": [
    {
      "id": "12345",
      "title": "Übungsblatt 2",
      "description": "Aufgaben 1-5",
      "due_date": "2024-01-15T23:59:00",
      "module_id": "section_123",
      "module_name": "Mathematik",
      "priority": 4,
      "completed": false,
      "labels": ["abgabe"]
    }
  ],
  "modules": [
    {
      "id": "section_123",
      "name": "Mathematik",
      "total": 5,
      "completed": 2,
      "upcoming": 3
    }
  ],
  "last_sync": "2024-01-10T12:30:00"
}
```

---

## 🎯 Workflow-Beispiele

### Neue Abgabe hinzufügen

1. Öffne Todoist
2. Wähle Projekt "UNI"
3. Wähle Section (Modul)
4. Erstelle Task:
   ```
   Übungsblatt 3 #abgabe
   Fällig: 22. Januar 23:59
   ```
5. Warte auf nächsten Sync (max. 5 Min)

### Abgabe als erledigt markieren

1. Öffne Todoist
2. Hake Task ab ✅
3. Task verschwindet aus Wochenansicht
4. Modul-Fortschritt wird aktualisiert

### Fälligkeitsdatum ändern

1. Öffne Task in Todoist
2. Klicke auf Datum
3. Wähle neues Datum
4. Änderung wird beim nächsten Sync übernommen

---

## 🔍 Debugging

### Backend-Logs prüfen

```bash
# Manueller Start (mit Logs)
cd MMM-UniAssignments
./start-backend.sh

# Systemd Service Logs
sudo journalctl -u mmm-uni-assignments -f
```

### Sync-Test

```bash
cd MMM-UniAssignments/backend
source venv/bin/activate
python3 todoist_sync.py
```

**Erwartete Ausgabe:**
```
Syncing Todoist project: UNI
Project ID: 123456789
Loaded 3 sections (modules)
Loaded 8 assignments

✅ Sync completed!
Found 8 assignments

Next 3 assignments:
  - Übungsblatt 2 (Mathematik) - Due: 2024-01-15
  - Laborprotokoll (Physik) - Due: 2024-01-18
  - Probeklausur (Mathematik) - Due: 2024-01-25

Modules: 3
  - Mathematik: 2/5 completed
  - Informatik: 1/2 completed
  - Physik: 0/1 completed
```

### Häufige Probleme

**"Project 'UNI' not found"**
- Projekt existiert nicht
- Prüfe Schreibweise in `.env` (case-sensitive)

**"No assignments found"**
- Keine Tasks mit Label `abgabe`
- Prüfe Label-Konfiguration in `.env`

**"Invalid API token"**
- Token ist falsch oder abgelaufen
- Hole neuen Token von Todoist

---

## 🔒 Sicherheit

### Token-Schutz

✅ **Do:**
- Token in `.env` speichern
- `.env` in `.gitignore` eintragen
- Backup von `.env` an sicherem Ort

❌ **Don't:**
- Token in Code hardcoden
- Token in Git committen
- Token öffentlich teilen

### Berechtigungen

Der API Token hat **vollen Zugriff** auf deinen Todoist-Account:
- Lesen aller Projekte ✅
- Schreiben/Löschen möglich ⚠️

Das Backend nutzt nur **Read-Only** Operationen.

---

## 🎨 Anpassungen

### Projekt-Name ändern

```env
# .env
TODOIST_PROJECT=Studium
```

### Label ändern

```env
# .env
ASSIGNMENT_LABEL=deadline
```

### Mehrere Projekte

Aktuell wird nur ein Projekt unterstützt.

**Workaround:** Sections in verschiedenen Projekten mit gleichem Label.

---

## 📱 Mobile App

### Quick Add

Nutze Todoist Quick Add für schnelles Erstellen:

```
Übungsblatt 4 #abgabe #UNI/Mathematik morgen 23:59
```

Dies erstellt:
- Task "Übungsblatt 4"
- In Projekt "UNI"
- Section "Mathematik"
- Label "abgabe"
- Fällig: Morgen 23:59

---

## 🔮 Zukunftspläne

- [ ] Mehrere Projekte
- [ ] Custom Labels pro Ansicht
- [ ] Sub-Tasks Support
- [ ] Kommentare anzeigen
- [ ] Push-Benachrichtigungen
- [ ] Bidirektionale Sync (Tasks im Mirror abhaken)
