# RN Deckenbewehrung

Entwicklungsstand **0.1.0** für ein Allplan-2026-PythonPart mit FRILO-FEM-Anbindung.
Das Repository enthält ausführbaren Rechen- und Optimierungscode sowie eine
Allplan-Diagnosepalette. **Das vollständige Bewehrungsplugin ist noch nicht
fertig; die Palette erzeugt noch keine Bewehrung.**

```sh
python -m pip install -e ".[test]"
python -m pytest -q
rn-demo examples/fem-test.json --output demo-report.json
python tools/package.py
```

- [Implementierungsstatus und offene Funktionen](docs/STATUS.md)
- [Installation](docs/INSTALLATION.md)
- [Bedienung, lokale Tests und Fehlerdiagnose](docs/BEDIENUNG-UND-TESTS.md)
- [Architektur, Einheiten und Optimierungsfunktion](docs/ARCHITEKTUR.md)
- [Verifizierte Allplan-API-Quellen](docs/API-NACHWEIS.md)
- [Originalanforderungen](docs/ANFORDERUNGEN.md)

Der FRILO-ASF-Import benötigt noch eine repräsentative Datei sowie FRILO-Modul,
Version und Exportangaben. Es gibt keinen erfundenen ASF-Parser und keine
ungeprüften automatischen Verankerungsformeln.

Allplan-Abhängigkeiten sind vom Rechenkern getrennt. Der Rechenkern verwendet
Shapely 2; die Diagnosepalette benötigt ausschließlich das Allplan-SDK.
Allplan 2027 ist architektonisch vorbereitet, aber nicht freigegeben.
