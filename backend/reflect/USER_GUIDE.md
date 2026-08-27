# Reflect - Self-Improving Skills System
## Benutzer-Guide

*"Correct once, never again"* - Ein System, das aus Ihren Korrekturen lernt und Claude Code kontinuierlich verbessert.

---

## 📖 Inhaltsverzeichnis

1. [Was ist Reflect?](#was-ist-reflect)
2. [Quick Start](#quick-start)
3. [Die drei Nutzungsmodi](#die-drei-nutzungsmodi)
4. [Praktische Beispiele](#praktische-beispiele)
5. [Confidence Levels erklärt](#confidence-levels-erklärt)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Was ist Reflect?

Reflect ist ein intelligentes Lernsystem für Claude Code, das:

- **Korrekturen erkennt** wenn Sie Claude korrigieren
- **Patterns identifiziert** wenn bestimmte Ansätze gut funktionieren
- **Skills aktualisiert** basierend auf Ihrem Feedback
- **Git-History führt** damit Sie Änderungen nachverfolgen können

### Das Problem

Normalerweise wiederholt Claude dieselben Fehler in jeder neuen Session:

```
Session 1: Claude verwendet pip
Sie:      "Nein, verwende uv statt pip"
Claude:   "Ok, ich verwende jetzt uv"

Session 2: Claude verwendet wieder pip 😞
Sie:      "Ich hab dir doch gesagt, verwende uv!"
```

### Die Lösung

Mit Reflect lernt Claude dauerhaft:

```
Session 1: Claude verwendet pip
Sie:      "Nein, verwende uv statt pip"
Claude:   Führt /reflect aus → Aktualisiert Python-Skill

Session 2: Claude verwendet automatisch uv ✅
Session 3: Claude verwendet automatisch uv ✅
Session N: Claude verwendet automatisch uv ✅
```

---

## Quick Start

### 1. Status prüfen

```bash
/reflect-status
```

Zeigt:
- Ob Auto-Reflection aktiv ist
- Wann die letzte Analyse war
- Verfügbare Commands

### 2. Erste manuelle Reflection

Nachdem Sie Claude in einer Session korrigiert haben:

```bash
/reflect
```

Sie sehen dann:
1. **Detected Signals** - Was erkannt wurde
2. **Proposed Changes** - Diff der vorgeschlagenen Änderungen
3. **Approval Prompt** - [A]pprove / [M]odify / [S]kip / [Q]uit

### 3. Auto-Reflection aktivieren (optional)

Wenn Sie möchten, dass Reflection bei jedem Session-Ende automatisch läuft:

```bash
/reflect-on
```

Deaktivieren:

```bash
/reflect-off
```

---

## Die drei Nutzungsmodi

### 🔧 Modus 1: Manual Reflection

**Wann verwenden?**
- Sie haben Claude gerade korrigiert
- Sie wollen gezielt eine Session analysieren
- Sie wollen volle Kontrolle über jeden Schritt

**Wie verwenden?**

```bash
# Analysiere die aktuelle Session
/reflect

# Analysiere nur einen bestimmten Skill
/reflect python-project-creator
```

**Workflow:**
1. Sie arbeiten mit Claude und korrigieren Fehler
2. Am Ende der Session: `/reflect`
3. Review der erkannten Signale und Änderungen
4. Approval mit `A` (Approve), `M` (Modify), `S` (Skip) oder `Q` (Quit)
5. Skills werden aktualisiert und committed

**Vorteile:**
- ✅ Volle Kontrolle
- ✅ Gezieltes Lernen
- ✅ Keine Überraschungen

**Nachteile:**
- ❌ Manueller Aufwand
- ❌ Kann vergessen werden

---

### 🤖 Modus 2: Automatic Reflection

**Wann verwenden?**
- Sie arbeiten täglich intensiv mit Claude
- Sie wollen kontinuierliches Lernen ohne manuelle Schritte
- Sie vertrauen dem System

**Wie aktivieren?**

```bash
/reflect-on
```

**Workflow:**
1. Sie arbeiten ganz normal mit Claude
2. Bei Session-Ende: Reflection läuft automatisch im Hintergrund
3. Nächste Session: Sie sehen eine Benachrichtigung falls Skills aktualisiert wurden
4. Änderungen sind bereits committed

**Vorteile:**
- ✅ Automatisches Lernen
- ✅ Kein manueller Aufwand
- ✅ Kontinuierliche Verbesserung

**Nachteile:**
- ❌ Weniger Kontrolle
- ❌ Läuft im Hintergrund (kann übersehen werden)

**Wichtig:** Im Auto-Modus sehen Sie die Review NICHT während der Session. Das System committed automatisch. Prüfen Sie regelmäßig die Git-History:

```bash
cd ~/.claude/skills
git log --oneline
```

---

### ⚙️ Modus 3: Toggle System

**Commands:**

```bash
/reflect-on      # Auto-Reflection aktivieren
/reflect-off     # Auto-Reflection deaktivieren
/reflect-status  # Aktuellen Status anzeigen
```

**Status-Ausgabe:**

```
═══════════════════════════════════════════════════════════
                    REFLECTION STATUS
═══════════════════════════════════════════════════════════

Status:        ✓ Aktiviert
Mode:          Automatisch (bei Session-Ende)
Konfiguriert:  2026-01-05T14:23:15Z
Letzte Analyse: 2026-01-05T14:20:00

───────────────────────────────────────────────────────────
Commands:
  /reflect           - Manuelle Analyse der aktuellen Session
  /reflect-on        - Auto-Reflection aktivieren
  /reflect-off       - Auto-Reflection deaktivieren
  /reflect-status    - Status anzeigen (dieser Befehl)
═══════════════════════════════════════════════════════════
```

**Empfohlener Workflow:**

1. **Erste Wochen**: Manuell (`/reflect`) um das System kennenzulernen
2. **Nach Eingewöhnung**: Auto-Modus (`/reflect-on`) für kontinuierliches Lernen
3. **Bei Bedarf**: Deaktivieren (`/reflect-off`) für wichtige/experimentelle Sessions

---

## Praktische Beispiele

### Beispiel 1: Korrektur eines falschen Tools

**Session-Verlauf:**

```
User: Erstelle ein Python-Projekt

Claude: Ich verwende pip install für die Dependencies...
*verwendet pip*

User: Nein, verwende bitte uv statt pip. Uv ist schneller und moderner.

Claude: Verstanden, ich verwende jetzt uv install...
*verwendet uv*
```

**Reflection ausführen:**

```bash
/reflect
```

**Erkanntes Signal:**

```
═══════════════════════════════════════════════════════════
REFLECTION REVIEW
═══════════════════════════════════════════════════════════

## Signals Detected

**python-project-creator**:
  - HIGH: 1 corrections

───────────────────────────────────────────────────────────

## python-project-creator

```diff
--- python-project-creator/SKILL.md (current)
+++ python-project-creator/SKILL.md (proposed)
@@ -15,6 +15,12 @@

 # Python Project Creator

+## Critical Corrections
+
+**Use 'uv' instead of 'pip'**
+
+- ✗ Don't: pip install
+- ✓ Do: uv install
+
 ## Overview
```

[A]pprove / [M]odify / [S]kip / [Q]uit? A

✓ Approved changes to python-project-creator
✓ Updated python-project-creator
✓ Changes committed to git

✓ 1 skill(s) updated successfully
```

**Ergebnis:** Ab jetzt verwendet Claude automatisch `uv` statt `pip` in Python-Projekten!

---

### Beispiel 2: Approval eines guten Patterns

**Session-Verlauf:**

```
User: Schreibe Tests für die API

Claude: Ich strukturiere die Tests mit pytest in folgende Kategorien:
- test_unit/ für Unit-Tests
- test_integration/ für Integration-Tests
- test_e2e/ für End-to-End-Tests

User: Ja, perfekt! Diese Struktur ist sehr übersichtlich.
```

**Reflection:**

```bash
/reflect
```

**Erkanntes Signal:**

```
## Signals Detected

**testing-framework**:
  - MEDIUM: 1 approvals

## testing-framework

```diff
+## Best Practices
+
+- Approved approach: Structure tests with pytest in categories: test_unit/, test_integration/, test_e2e/
```

**Ergebnis:** Pattern wird als Best Practice dokumentiert.

---

### Beispiel 3: Überlegung für zukünftige Verbesserungen

**Session-Verlauf:**

```
User: Die Error-Handling könnte verbessert werden

Claude: Wie möchten Sie die Error-Handling verbessern?

User: Have you considered using custom exception classes statt generic try-catch blocks?

Claude: Gute Idee! Das würde die Fehler spezifischer machen.
```

**Reflection:**

```bash
/reflect
```

**Erkanntes Signal:**

```
## Signals Detected

**error-handling**:
  - LOW: 1 observations

## error-handling

```diff
+## Advanced Considerations
+
+- Consider: using custom exception classes statt generic try-catch blocks
```

**Ergebnis:** Wird als Überlegung notiert für zukünftige Referenz.

---

## Confidence Levels erklärt

Das System klassifiziert Signale in drei Confidence-Levels:

### 🔴 HIGH Confidence - Korrekturen

**Erkennungspatterns:**
- "Nein, verwende X statt Y"
- "Tatsächlich ist es X, nicht Y"
- "Niemals X tun"
- "Immer X prüfen"

**Aktion:** Erstellt "Critical Corrections" Sektion mit ✗/✓ Vergleich

**Beispiele:**
```
❌ "Nein, der Button heißt 'SubmitButton' nicht 'SendButton'"
❌ "Verwende uv statt pip"
❌ "Niemals Credentials hardcoden"
❌ "Immer SQL-Injections prüfen"
```

**Verwendung:** Für faktische Fehler und wichtige Regeln

---

### 🟡 MEDIUM Confidence - Approvals

**Erkennungspatterns:**
- "Ja, perfekt"
- "Das ist genau richtig"
- "Funktioniert gut"
- "Gute Arbeit"

**Aktion:** Fügt zu "Best Practices" Sektion hinzu

**Beispiele:**
```
✅ "Ja, diese Projektstruktur ist perfekt"
✅ "Das funktioniert sehr gut"
✅ "Genau so sollte es sein"
```

**Verwendung:** Für erfolgreiche Patterns und Ansätze

---

### 🟢 LOW Confidence - Überlegungen

**Erkennungspatterns:**
- "Have you considered..."
- "Was ist mit..."
- "Warum nicht versuchen..."

**Aktion:** Fügt zu "Advanced Considerations" hinzu

**Beispiele:**
```
💡 "Have you considered using TypeScript?"
💡 "Was ist mit Edge Cases?"
💡 "Warum nicht async/await verwenden?"
```

**Verwendung:** Für Vorschläge ohne sofortige Verpflichtung

---

## Best Practices

### ✅ Do's

1. **Erste Wochen manuell**
   - Verwenden Sie `/reflect` manuell
   - Lernen Sie das System kennen
   - Verstehen Sie, was erkannt wird

2. **Spezifisch korrigieren**
   ```
   ✅ "Verwende 'uv' statt 'pip'"
   ❌ "Das ist falsch"
   ```

3. **Kontext geben**
   ```
   ✅ "Verwende uv statt pip, weil es schneller ist"
   ❌ "Verwende uv"
   ```

4. **Git-History prüfen**
   ```bash
   cd ~/.claude/skills
   git log --oneline --graph
   git diff HEAD~1  # Letzte Änderung anzeigen
   ```

5. **Regelmäßig Status checken**
   ```bash
   /reflect-status
   ```

### ❌ Don'ts

1. **Nicht zu vage**
   ```
   ❌ "Das ist irgendwie nicht gut"
   ✅ "Verwende const statt var für Variablen"
   ```

2. **Nicht widersprüchlich**
   ```
   Session 1: "Verwende pip"
   Session 2: "Verwende uv"
   → Erstellt widersprüchliche Rules
   ```

3. **Nicht Auto-Modus sofort aktivieren**
   ```
   ❌ Tag 1: /reflect-on
   ✅ Tag 1-7: /reflect (manuell)
   ✅ Ab Tag 8: /reflect-on (wenn Sie es verstehen)
   ```

4. **Nicht Backups löschen**
   - Backups liegen in `~/.claude/skills/{skill-name}/.backups/`
   - Werden automatisch nach 30 Tagen gelöscht
   - Bei Problemen können Sie zurückrollen

---

## Troubleshooting

### Problem: "/reflect findet keine Signale"

**Symptom:**
```
✓ No improvement suggestions found
```

**Mögliche Ursachen:**

1. **Keine Korrekturen in der Session**
   - Lösung: Nur in Sessions mit tatsächlichen Korrekturen verwenden

2. **Korrekturen nicht erkannt**
   - Ihre Formulierung passt nicht zu den Patterns
   - Lösung: Verwenden Sie klarere Formulierungen:
     ```
     ✅ "Nein, verwende X statt Y"
     ❌ "Hmm, vielleicht könnte man..."
     ```

3. **Transcript nicht gefunden**
   - Lösung: Prüfen Sie `~/.claude/session-env/*/transcript.jsonl`

---

### Problem: "Skills werden nicht aktualisiert"

**Symptom:**
```
✗ Error updating skill-name: ...
```

**Mögliche Ursachen:**

1. **Skill-Datei korrupt**
   - Prüfen: `cat ~/.claude/skills/{skill-name}/SKILL.md`
   - Lösung: Aus Backup wiederherstellen:
     ```bash
     cp ~/.claude/skills/{skill-name}/.backups/SKILL_*.md \
        ~/.claude/skills/{skill-name}/SKILL.md
     ```

2. **Keine Schreibrechte**
   - Prüfen: `ls -la ~/.claude/skills/{skill-name}/`
   - Lösung: `chmod -R u+w ~/.claude/skills/`

3. **YAML-Fehler**
   - Die YAML-Frontmatter ist ungültig
   - Lösung: Validieren mit:
     ```bash
     python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"
     ```

---

### Problem: "Git-Commit schlägt fehl"

**Symptom:**
```
Warning: Git commit failed: ...
Changes were applied but not committed.
```

**Lösung:**

Manuell committen:

```bash
cd ~/.claude/skills
git status
git add .
git commit -m "Manual commit after reflection"
```

---

### Problem: "Auto-Reflection läuft nicht"

**Symptom:**
Kein Reflection bei Session-Ende

**Checkliste:**

1. **Ist Auto-Reflection aktiviert?**
   ```bash
   /reflect-status
   # Sollte zeigen: Status: ✓ Aktiviert
   ```

2. **Hook konfiguriert?**
   ```bash
   cat ~/.claude/settings.local.json | grep -A 10 hooks
   ```
   Sollte enthalten:
   ```json
   "hooks": {
     "Stop": [{
       "hooks": [{
         "command": "/Users/.../reflect/scripts/hook-stop.sh"
       }]
     }]
   }
   ```

3. **Script ausführbar?**
   ```bash
   ls -la ~/.claude/skills/reflect/scripts/hook-stop.sh
   # Sollte -rwxr-xr-x zeigen
   ```

4. **Log prüfen:**
   ```bash
   cat ~/.claude/reflect-hook.log
   ```

---

### Problem: "Rollback zu alter Version"

**Wenn Änderungen rückgängig gemacht werden sollen:**

**Option 1: Aus Backup wiederherstellen (letzte Stunden)**

```bash
cd ~/.claude/skills/{skill-name}/.backups
ls -lt  # Zeigt neueste Backups
cp SKILL_20260105_142030.md ../SKILL.md
```

**Option 2: Git-Reset (letzter Commit)**

```bash
cd ~/.claude/skills
git log --oneline  # Finde Commit vor der Änderung
git revert HEAD    # Macht letzten Commit rückgängig
```

**Option 3: Git-Reset (bestimmter Commit)**

```bash
cd ~/.claude/skills
git log --oneline
git checkout abc123f -- {skill-name}/SKILL.md
```

---

## FAQ

### F: Kann ich Reflection deaktivieren?

**A:** Ja! Das System ist standardmäßig deaktiviert.

- **Manual Mode**: Nur wenn Sie `/reflect` ausführen
- **Deaktivieren**: `/reflect-off`
- **Niemals aktiviert**: Einfach niemals `/reflect-on` ausführen

---

### F: Werden alle meine Korrekturen gespeichert?

**A:** Nein, nur die, die Sie approven:

1. System **erkennt** Korrekturen automatisch
2. System **schlägt vor** Änderungen
3. **Sie entscheiden** was applied wird (A/M/S/Q)
4. Nur approved Änderungen werden committed

---

### F: Kann ich die Patterns anpassen?

**A:** Ja! Editieren Sie:

```bash
~/.claude/skills/reflect/scripts/extract_signals.py
```

Fügen Sie eigene Regex-Patterns hinzu:

```python
CORRECTION_PATTERNS = [
    r"(?i)no,?\s+don't\s+(?:do|use)\s+(.+?)[,.]?\s+(?:do|use)\s+(.+)",
    r"(?i)YOUR_CUSTOM_PATTERN_HERE",  # ← Hier
]
```

Oder erweitern Sie die Pattern-Library:

```bash
~/.claude/skills/reflect/references/signal-patterns.md
```

---

### F: Wie sehe ich was gelernt wurde?

**A:** Mehrere Möglichkeiten:

**1. Git-History:**
```bash
cd ~/.claude/skills
git log --oneline --grep="reflection"
git show <commit-hash>
```

**2. Skill-Dateien direkt:**
```bash
cat ~/.claude/skills/{skill-name}/SKILL.md
```

**3. Git-Diff:**
```bash
cd ~/.claude/skills
git log --all --full-history --oneline -- {skill-name}/SKILL.md
git diff <commit1> <commit2> -- {skill-name}/SKILL.md
```

---

### F: Was passiert wenn ich widersprüchliche Korrekturen gebe?

**A:** Das System erkennt dies nicht automatisch. Best Practice:

1. **Manuelle Review vor Approval**
   - Lesen Sie die Diffs sorgfältig
   - Skip (`S`) widersprüchliche Änderungen

2. **Git-History prüfen**
   - Schauen Sie ob bereits eine Rule existiert
   - Entscheiden Sie welche behalten werden soll

3. **Manuelle Bereinigung**
   - Editieren Sie die Skill-Datei direkt
   - Committen Sie manuell

---

### F: Welche Skills werden analysiert?

**A:** Nur Skills die in der Session verwendet wurden:

- Skills die via `/skill-name` aufgerufen wurden
- Skills die via Skill-Tool verwendet wurden
- Plus: `general` als Fallback

**Filtern auf bestimmten Skill:**
```bash
/reflect python-project-creator
```

---

### F: Kann ich Reflection pausieren?

**A:** Ja, mehrere Optionen:

**Temporär (diese Session):**
- Einfach `/reflect` nicht ausführen (Manual Mode)
- Oder Skip (`S`) bei Review

**Dauerhaft:**
```bash
/reflect-off
```

**Für spezifische Sessions:**
- Deaktivieren vor Session: `/reflect-off`
- Nach Session reaktivieren: `/reflect-on`

---

### F: Wie viel Speicherplatz braucht das System?

**A:** Minimal:

- **Scripts**: ~50 KB
- **State-Files**: <1 KB
- **Backups**: ~5 KB pro Skill-Update (auto-cleanup nach 30 Tagen)
- **Git-Repo**: ~100 KB (wächst mit Commits)

**Gesamt: <1 MB** typischerweise

---

### F: Funktioniert es mit mehreren Projekten?

**A:** Ja! Das System ist global:

- Learnings gelten für **alle** Claude Code Sessions
- Unabhängig vom Projekt-Directory
- Skills in `~/.claude/skills/` sind global

**Pro-Projekt-Skills:**
Erstellen Sie projekt-spezifische Skills in `.claude/skills/` (lokal).

---

### F: Kann ich Learnings sharen/synchronisieren?

**A:** Ja, via Git:

**Setup Remote:**
```bash
cd ~/.claude/skills
git remote add origin <your-repo-url>
git push -u origin main
```

**Auf anderem Rechner:**
```bash
cd ~/.claude
git clone <your-repo-url> skills
```

**Sync:**
```bash
cd ~/.claude/skills
git pull   # Hole Updates
git push   # Pushe eigene Updates
```

**Achtung:** Bei Merge-Konflikten manuell resolven!

---

### F: Gibt es Performance-Probleme?

**A:** Normalerweise nein:

- **Manual Mode**: Nur wenn Sie `/reflect` ausführen (on-demand)
- **Auto Mode**: Läuft im Hintergrund, nicht-blockierend
- **Timeout**: Hook hat 5s Timeout, dann Background-Processing

**Bei langen Transcripts:**
- Extraktion kann 5-10s dauern
- Background-Process verhindert Session-Blockierung
- Check Log: `tail ~/.claude/reflect-hook.log`

---

## 🎓 Erweiterte Nutzung

### Custom Pattern hinzufügen

**Beispiel:** Deutsche Korrekturen erkennen

```bash
# Editieren Sie extract_signals.py
nano ~/.claude/skills/reflect/scripts/extract_signals.py
```

Fügen Sie hinzu:

```python
# Deutsche Korrektur-Patterns
CORRECTION_PATTERNS_DE = [
    r"(?i)nein,?\s+nicht\s+(.+?)[,.]?\s+sondern\s+(.+)",
    r"(?i)verwende\s+(.+?)\s+statt\s+(.+)",
]

# Kombinieren mit bestehenden
CORRECTION_PATTERNS.extend(CORRECTION_PATTERNS_DE)
```

---

### Skill-spezifische Exclusion

**Wenn bestimmte Skills nicht gelernt werden sollen:**

```bash
# Editieren Sie extract_signals.py
nano ~/.claude/skills/reflect/scripts/extract_signals.py
```

Fügen Sie Filterfunktion hinzu:

```python
EXCLUDED_SKILLS = ['experimental-skill', 'test-skill']

def group_by_skill(signals):
    grouped = {}
    for signal in signals:
        for skill in signal.get('skills', ['general']):
            if skill in EXCLUDED_SKILLS:  # ← Filter
                continue
            if skill not in grouped:
                grouped[skill] = []
            grouped[skill].append(signal)
    return grouped
```

---

### Notifications konfigurieren

**macOS Notification bei Updates:**

```bash
# Editieren Sie reflect.py
nano ~/.claude/skills/reflect/scripts/reflect.py
```

Fügen Sie nach erfolgreichem Update hinzu:

```python
import subprocess

def main():
    # ... existing code ...

    if success_count > 0:
        # macOS Notification
        subprocess.run([
            'osascript', '-e',
            f'display notification "{success_count} skill(s) updated" '
            f'with title "Reflect" sound name "Glass"'
        ])
```

---

## 📚 Weiterführende Ressourcen

### Dateien zum Studieren

1. **Pattern-Library:**
   ```
   ~/.claude/skills/reflect/references/signal-patterns.md
   ```

2. **Scripts:**
   ```
   ~/.claude/skills/reflect/scripts/extract_signals.py    # Pattern-Detection
   ~/.claude/skills/reflect/scripts/update_skill.py       # Skill-Updates
   ~/.claude/skills/reflect/scripts/present_review.py     # Review-UI
   ```

3. **Git-History:**
   ```bash
   cd ~/.claude/skills
   git log --graph --oneline --all
   ```

### Debug-Modus

**Verbose Logging aktivieren:**

```bash
# Temporär für einen Test
TRANSCRIPT_PATH=/path/to/transcript.jsonl \
  python3 ~/.claude/skills/reflect/scripts/reflect.py
```

**Log-Datei prüfen:**

```bash
tail -f ~/.claude/reflect-hook.log
```

---

## 🎯 Zusammenfassung

### Schnellreferenz

| Command | Funktion |
|---------|----------|
| `/reflect` | Manuelle Analyse der Session |
| `/reflect <skill>` | Analysiere nur einen Skill |
| `/reflect-on` | Auto-Reflection aktivieren |
| `/reflect-off` | Auto-Reflection deaktivieren |
| `/reflect-status` | Status anzeigen |

### Review-Optionen

| Taste | Aktion |
|-------|--------|
| `A` | Approve (Alle Änderungen übernehmen) |
| `M` | Modify (Mit Natural Language modifizieren) |
| `S` | Skip (Diesen Skill überspringen) |
| `Q` | Quit (Review abbrechen) |

### Wichtige Pfade

```
~/.claude/skills/reflect/              # Reflect Skill
~/.claude/skills/reflect/.state/       # Status & Locks
~/.claude/skills/{skill}/.backups/     # Backups (30 Tage)
~/.claude/settings.local.json          # Hook-Konfiguration
~/.claude/reflect-hook.log             # Hook-Logs
```

---

## 💡 Tipps für optimale Nutzung

1. **Erste Woche**: Täglich `/reflect` manuell → System kennenlernen
2. **Zweite Woche**: `/reflect-on` aktivieren → Automatisches Lernen
3. **Regelmäßig**: Git-History prüfen → Was wurde gelernt?
4. **Bei Fehlern**: Backups nutzen → Schnelle Wiederherstellung
5. **Teilen**: Git-Repo → Learnings synchronisieren

**Viel Erfolg mit dem Self-Improving Skills System!** 🚀

---

*Letzte Aktualisierung: 2026-01-05*
*Version: 1.0.0*
