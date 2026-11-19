# RN Deckenbewehrung

Entwicklungsstand **0.2.0** für ein Allplan-2026-PythonPart mit FRILO-FEM-Anbindung.
Das Repository enthält ausführbaren Rechen- und Optimierungscode sowie eine
Allplan-Diagnosepalette. **Das vollständige Bewehrungsplugin ist noch nicht
fertig; die Palette erzeugt noch keine Bewehrung.**

```sh
python -m pip install -e ".[test]"
python -m pytest -q
rn-demo examples/fem-test.json --output demo-report.json
rn-asf-inspect "meine-decke.asf" --output asf-pruefbericht.json
python tools/package.py
```

- [Implementierungsstatus und offene Funktionen](docs/STATUS.md)
- [Installation](docs/INSTALLATION.md)
- [Bedienung, lokale Tests und Fehlerdiagnose](docs/BEDIENUNG-UND-TESTS.md)
- [Architektur, Einheiten und Optimierungsfunktion](docs/ARCHITEKTUR.md)
- [Verifizierte Allplan-API-Quellen](docs/API-NACHWEIS.md)
- [Originalanforderungen](docs/ANFORDERUNGEN.md)

Der echte ALLPLOT-5.0-Strukturleser ist mit der bereitgestellten FRILO-Datei
geprüft. Die Zuordnung der QM1-Spalten und Einheiten ist noch nicht freigegeben.
Siehe [ASF-Format und Grenzen](docs/ASF-FORMAT.md). Neu sind außerdem
Deckenkörperprüfung, Grundstabplanung und rechteckige Mattenaufteilung.

Allplan-Abhängigkeiten sind vom Rechenkern getrennt. Der Rechenkern verwendet
Shapely 2; die Diagnosepalette benötigt ausschließlich das Allplan-SDK.
Allplan 2027 ist architektonisch vorbereitet, aber nicht freigegeben.
