# Implementierungsstatus 0.3.0

**Weiterhin Entwicklungsstand, keine vollständige produktive
Bewehrungserzeugung.** Der Einstieg prüft nun Deckengeometrie und echte ASF-
Dateien. Die automatische Erzeugung bleibt gesperrt.

## Neu in 0.3 – externer Prüflauf

- Räumlich indizierte FEM-Rasterauswertung mit konservativen Maximalwerten,
  nach oben gerundeten As-Stufen und begrenzten Rechteckbereichen.
- Explizite Geometrien für fehlende FEM-Ergebnisse und problematische Rand-/
  Öffnungsbereiche; alle fehlgeschlagenen Verlegevorschläge im Prüfbericht.
- Optionale protokollierte Randkorrektur mit explizitem Abstands- und Flächenlimit.
- `rn-review` verbindet Projekt-JSON, Importfreigabe, Bereichsbildung,
  Kandidatenbewertung und JSON-Prüfbericht. Realimport verlangt ein geprüftes,
  an den Datei-Hash gebundenes Ergebnisprofil. Kein voreingestelltes FRILO-Profil.
- Allplan-Palette unverändert auf Diagnosestand; diese Funktionen laufen im
  externen Rechenkern. Siehe PRUEFLAUF.md für Umfang und Grenzen.

## Vollständig implementiert und getestet – begrenzter Rechenumfang

- Bisheriger Kern: vier Kanäle, Querschnitte, aktive Lagen kompakt anordnen,
  Polygongeometrie mit Öffnungen, Stabzuschnitt, konservative Grundanrechnung,
  Zulagebedarf, begrenzte Bereichszusammenfassung und Kandidatenoptimierung.
- Echter struktureller ASF-Leser für den beobachteten ALLPLOT-5.0-Dialekt:
  Konturen, Knoten, Elemente, rohe QM1/QR3-Daten und Materialtabellen;
  vollständiger Lauf mit der bereitgestellten 20-MB-Datei erfolgreich.
- Explizite Importprofile und Koordinatenabgleich, keine geratene QM1-Zuordnung.
- Prismatische Deckenkörper aus Weltkoordinaten: UK, OK, Dicke, Randkonturen
  einschließlich Durchbrüchen; Ablehnung offener, schiefer und verjüngter Körper.
- Grundstab-Verlegeplan mit tatsächlichen Höhen, Aussparungsunterbrechungen,
  Lieferlängenprüfung und lokalen Formpositionsnummern. Keine automatische
  Stoßplanung/Verankerungsfreigabe oder vorhandene Modellpositionsinventur.
- Rechteckige Mattenaufteilung mit expliziten Längs-/Querübergreifungen und
  Randzuschnitt. Öffnungen/nichtrechteckige Flächen werden derzeit abgelehnt.
- CLI `rn-asf-inspect` und bestehende synthetische Demo/SVG-Prüfvorschau.

## Implementiert, Allplan-Integrationstest ausstehend

- Deckenfilter und Script-Object-Workflow.
- Polyhedron3D-Adapter mit dokumentierten globalen Eckpunktzugriffen und
  Übernahme der geometrisch geprüften UK/OK/Dicke in die Palette.
- ASF-Dateiauswahl und Anzeige der gelesenen Knoten-/Element-/Ergebniszahlen.
- Native Einzelstab-/Einzelmattenfabriken. Brücke vom Grundstabplan zur
  nativen Elementliste mit übergebenen Format-/Layereigenschaften und
  Prüfung gegen übergebene belegte Positionsnummern. Kein Modellschreibaufruf.
- Manuelles Diagnosepaket mit gebündelten Standardbibliotheks-Modulen;
  keine Shapely-Installation im Allplan-Prozess für diese Prüfungen nötig.

## Weitere Daten oder Entscheidungen erforderlich

- Die ASF-Beispieldatei liegt jetzt vor. Noch erforderlich: verifizierte
  QM1/QR3-Semantik, Exporteinheiten und FRILO-Modul/-Version. Siehe ASF-FORMAT.md.
- Gewählte Normausgabe, Nationaler Anhang und verifizierte Regeln/Nachweise
  für Verbund, Verankerung und Stöße. Keine pauschale 40d/50d-Automatik.
- Lokaler Allplan-2026-Test von tatsächlicher Architekturmodellgeometrie,
  Öffnungen, SDK, Katalog, Palette und nativen Bewehrungselementen.

## Noch nicht umgesetzt

- Produktiver ASF→Zulagen-Workflow mit freigegebener Ergebnisinterpretation.
- Betonattributauswertung, Mehrfachdeckenauswahl, BRep-/gekrümmte Geometrie.
- Normberechnung, Stöße, Grundbewehrungs-Wirksamkeitsnachweis, räumliche
  Kollisionen von Grundbewehrung/Zulagen, Öffnungsrand-/Eckbewehrung.
- Mattenzuschnitt um Öffnungen, Mattenrotation und vollständige Katalogauswertung.
- Interaktive Allplan-Heatmap und bearbeitbare Zulagebereiche.
- Tatsächliche Layerauswahl/-auflösung, globale Positionsinventur,
  transaktionales Erzeugen, persistente Elementzuordnung und sichere Löschung.
- Plugin-Manager-Paket, Einbindung der Dokumentations-SVGs, Allplan 2027-Test.
