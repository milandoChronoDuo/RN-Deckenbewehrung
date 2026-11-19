# Installation des Entwicklungsstands

## Rechenkern (ohne Allplan)

Python 3.11 oder neuer:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e ".[test]"
python -m pytest -q
rn-demo examples/fem-test.json --output demo-report.json
```

## Diagnosepalette in Allplan 2026

1. `python tools/package.py` erzeugt `dist/RN-Deckenbewehrung-0.1.0-diagnose.zip`.
2. ZIP entpacken. Zuerst in einem Testprojekt verwenden.
3. Die beiden Python-Dateien aus `allplan/PythonPartsScripts/RN` in einen
   vom lokalen Allplan-2026-PythonParts-System verwendeten Script-Suchpfad
   unter `RN` kopieren. Üblicherweise wird der Bürostandard unter
   `STD/PythonPartsScripts` verwendet; den tatsächlichen Pfad mit Allmenu
   beziehungsweise der lokalen PythonParts-Einrichtung prüfen.
4. Den Ordner `allplan/Library/RN` in die entsprechende Büro-/Benutzerbibliothek
   kopieren. Die PYP referenziert `RN\Deckenbewehrung.py`.
5. Allplan neu starten oder die Bibliothek aktualisieren. PythonPart öffnen,
   eine einschichtige Decke anklicken und Dicke/Status prüfen.

Der Diagnosestand schreibt keine Bewehrung. Gesperrte Felder sind keine
funktionierenden Planungseingaben. Ein vollständiger Ein-Klick-Installer oder
Plugin-Manager-Import wird nicht behauptet; dessen Paketformat wurde noch nicht
verifiziert. Allplan 2027 wird vom Versionsfilter noch nicht freigegeben.
