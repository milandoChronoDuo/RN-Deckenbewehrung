# Implementierungsstatus 0.1.0

Dieser Stand ist ein Entwicklungsfundament, **kein benutzbares vollständiges
Bewehrungsplugin**. Die Allplan-Palette erzeugt absichtlich keine Elemente.

## Vollständig implementiert und getestet (jeweils im angegebenen Umfang)

- Validierte Stabquerschnitte, mm ↔ cm²/m und vier unabhängige Ergebniskanäle.
- Aktive Lagen kompakt anordnen; Richtung deaktivierter erster Lage verändert
  die zweite Lage nicht. Einfache vertikale Kollisionsprüfung.
- Ebene Polygonkontur mit mehreren polygonalen Öffnungen, konkave Konturen,
  Stabachsen mit Randabstand und Aufteilung an Öffnungen. Kreise können als
  ausreichend genaue Polygone übergeben werden; kein Allplan-Kreisimport.
- Mattenkatalog-Datenschnittstelle mit getrenntem As X/Y und „keine Matte“.
  Das ist kein Zugriff auf den aktiven Allplan-Katalog.
- Konservative, räumlich begrenzte Grundbewehrungsanrechnung. Wirksame Flächen
  müssen extern geprüft sein. Teilüberdeckte FEM-Zellen erhalten kein Guthaben.
- Synthetisches JSON-FEM-Format mit vier Werten je Zelle, Einheiten, Deckenbezug,
  Koordinatenbestätigung, Öffnungs- und Überlappungsprüfung.
- Zulagebedarf, geometrischer Bereichsabstand, begrenzte Rechteckzusammenfassung.
- Kandidatenoptimierung für Rechtecke: As, Abstand, lichter Abstand,
  geometrisch mögliche Endverankerungen, maximale Stablänge, Masse und Aufwand.
- Explizite projektspezifische Verankerungs-/Stoßwerte mit Nachweisreferenz;
  keine normativen Formeln. Stoßlängen werden gespeichert, noch nicht verlegt.
- Vorschau-Bestätigungslogik und Sperre bei vorhandenen Erzeugungskennungen
  als reine Domänenlogik, ohne persistente Allplan-Anbindung.
- JSON-Demobericht; SVG-Prüfvorschau für einen Ergebniskanal.

## Implementiert, Allplan-Integrationstest ausstehend

- Script-Object mit SingleElementSelectInteractor und Deckenfilter.
- Einlesen der Dicke einschichtiger Decken; keine Verifikation horizontaler Lage.
- Deutsche Diagnosepalette, Umschaltung Matten/Rundstahl; Planungsfelder sind
  gesperrt, weil sie noch keine Erzeugung steuern. XML-Schema geprüft.
- Native Fabriken für einen horizontalen Einzelstab und eine rechteckige
  Katalogmatte. Nicht mit Deckenauswahl oder Schreibvorgängen verbunden.
- Manuelles Diagnose-Installationspaket; kein produktiver Installer.

## Weitere Daten oder Entscheidungen erforderlich

- Repräsentative **FRILO-ASF-Datei**, FRILO-Modul und Version, Exportoptionen,
  Einheiten und zugehörige Modellkontur. ASF wird ausdrücklich abgelehnt.
- Normausgabe und Nationaler Anhang sowie verifizierte Bemessungsgrundlagen für
  Verbund, Verankerung, Stöße und konstruktive Grenzen.
- Lokales Allplan 2026 für Tests von SDK-Laufzeit, Palettenzuständen,
  Geometrieauswertung, Mattenkatalog und Bewehrungsdarstellung.

## Noch nicht umgesetzt

- Vollständige Deckenauswertung einschließlich globaler UK/OK, Öffnungen,
  Betonattributen, schiefen Flächen und zusammenhängender Mehrfachauswahl.
- FRILO-ASF-Parser und Alternative über offiziellen FEM-Import.
- Produktive Grundbewehrung, Mattenaufteilung/-stöße, Drehung von Matten und
  Ermittlung tatsächlich wirksamer Bereiche aus erzeugten Elementen.
- Automatische Normbemessung und automatische Stabstoßplanung.
- Zulagenhöhen und Kollisionsprüfung zwischen Grundbewehrung und Zulagen;
  polygonale Zulagenzerlegung; Öffnungsrand-/Eckbewehrung.
- Allplan-Heatmap, interaktive Auswahl, Verschieben, Teilen, Löschen und
  anschließende Nachprüfung von Zulagen.
- Layerauflösung, globale Positionsnummernverwaltung, transaktionale
  Modellerzeugung, persistente Eigentümerkennungen, sichere Löschung.
- Plugin-Manager-Paket und Einbindung der SVG-Hilfen in die Palette.
- Allplan 2027-Kompatibilitätsprüfung.

Es gibt keine automatische Löschfunktion und keine produktive Schreibfunktion.
Eine bestandene Domänenprüfung ist keine Ausführungsfreigabe.

## Grafische Quellen

16 eigene SVG-Icons und sechs beschriftete technische SVG-Schemata unter
`docs/assets`, reproduzierbar mit `tools/make_assets.py`. Sie sind Dokumentations-
assets; unterstützte Allplan-Bitmapformate, Größen und Einbindung sind noch
nicht verifiziert. Die SVG-Vorschau dient der externen Prüfung der Testdaten.
