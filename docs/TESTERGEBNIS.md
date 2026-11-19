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

## Version 0.2.0 – 19.11.2026

- 67 automatisierte Tests bestanden (Python 3.12.14), einschließlich echter
  Parserlogik an synthetischen ALLPLOT-Dateien, CP1252, Dreiecken, defekten IDs,
  Ergebniszuordnung, Koordinatenabgleich, Mattenaufteilung und prismatischen
  Körpern mit Öffnung. Allplan-Adapter mit Testdouble auf globalen Zugriff
  geprüft; dies ist kein SDK-Laufzeittest.
- Die bereitgestellte Original-ASF (20.222 MB dezimal) lokal vollständig
  strukturell eingelesen: 8.757 Knoten, 8.506 Elemente, 8.506 QM1-Datensätze.
- Alle 8.506 Elementpolygone gültig; 311 Dreiecke; sieben Öffnungen.
  Netz-/Konturflächenabweichung < 0.000001 in Quadrat-Dateieinheiten.
  Keine As-Spalteninterpretation oder Einheitenfreigabe daraus abgeleitet.
- `rn-asf-inspect` mit Originaldatei, bisherige `rn-demo`, Paketinstallation,
  Syntaxprüfung, Diagnose-ZIP und offizielle PYP-XSD-Validierung erfolgreich.
- Originaldatei, Prüfbericht mit Projektwerten und gerenderte Geometrie bleiben
  außerhalb des öffentlichen Repositorys.
