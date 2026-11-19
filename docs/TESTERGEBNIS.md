# Ausgeführte Prüfungen

19.11.2026, Linux, Python 3.12.14, Shapely 2 / GEOS:

- `pytest -q`: **45 bestanden**.
- `python -m compileall -q src allplan tools`: erfolgreich. Dies prüft nur Syntax,
  keine Imports oder Allplan-Signaturen zur Laufzeit.
- PYP gegen offizielle 2026-Schemata mit lxml.XMLSchema: gültig.
- Paketinstallation `pip install -e '.[test]'`: erfolgreich.
- `rn-demo examples/fem-test.json --output /tmp/rn-demo-report.json`: erfolgreich.
- `python tools/package.py`: Diagnose-ZIP erstellt.
- `git diff --check`: keine Whitespace-Fehler.

GitHub Actions ist für Python 3.11, 3.12 und 3.13 konfiguriert. Ein lokaler Lauf
auf 3.12 ist kein Nachweis für die anderen Versionen; deren Ergebnisse stehen
in GitHub Actions. Allplan wurde hier nicht ausgeführt.

Eine Quelltextprüfung der Palette ersetzt keine visuelle oder interaktive
Prüfung in Allplan. SVGs werden syntaktisch geprüft, nicht als eingebundene
Allplan-Assets getestet.
