# Reproduzierbarer Prüflauf (Version 0.3)

```sh
python -m pip install -e ".[test]"
rn-review examples/review-project.json --output review-report.json
```

Das mitgelieferte Projekt ist synthetisch. Es erzeugt drei Vorschläge und einen
Prüfpunkt für fehlende FEM-Ergebnisse. Es ist kein Beispiel einer vollständig
bemessenen Decke. Der Ergebnisbericht setzt `production_ready` stets auf false.

## Bereichsbildung

`rectangular_regions` verarbeitet echte Dreiecks-/Viereckzellen nach erfolgter
Importfreigabe oder synthetische Testzellen. Ein STRtree begrenzt die Suche auf
räumlich relevante Zellen. Jeder Rasterbereich erhält den höchsten darin
auftretenden zusätzlichen Bedarf. As-Stufen werden ausschließlich aufgerundet.
Die Rasterung kann daher Stahlmehrmengen erzeugen, unterschätzt aber keine
lokalen Bedarfsspitzen durch Mittelung. Geometrische Schnittflächen bis
1e-6 mm² gelten als numerische Nullflächen.

Gleichwertige benachbarte Rasterfelder werden deterministisch zu Rechtecken
zusammengefasst; beide Ausdehnungen sind begrenzt. Das ist eine zusätzliche
Bereichsbildung für unregelmäßige FEM-Netze. Die bisherige frei einstellbare
Abstandszusammenfassung bleibt separat und wird in diesem Prüflauf nicht
angewendet. Es gibt keinen behaupteten global optimalen Verlegeplan.

Rasterfelder, die Öffnungen oder Außenränder schneiden, werden als räumlich
markierte Prüfpunkte ausgegeben. Es entstehen dort keine Rechtecke über Löcher.
Nicht von FEM-Zellen abgedeckte Bereiche bleiben ausdrücklich unbekannt, auch
wenn benachbarte As-Werte null sind. Bei fehlender Verankerung oder unzulässiger
Kombination bleibt der betroffene Bereich mit Ursache im Bericht erhalten;
andere erfolgreiche Vorschläge täuschen keinen Gesamterfolg vor.

## Projektdatei

`RN-PROJECT-1` verwendet mm und cm²/m. Die JSON-Beispieldatei enthält Decke als
GeoJSON-Polygon (Innenringe für Öffnungen), Dicke/UK, Kombinationen, geprüfte
Verankerungswerte und Rasterparameter. `reviewed_lengths_mm` enthält im Beispiel
nur ausdrücklich synthetische Werte. Für echte Projekte sind projektspezifische
Nachweise nötig. Die CLI rechnet in 0.3 konservativ ohne Grundbewehrungsguthaben;
wirksame Grundbewehrungsbereiche sind über die Python-Schnittstelle `bases`
anschließbar, aber noch nicht über die Projektdatei eingebbar.

Für `fem.type = allplot5` sind zusätzlich erforderlich:

- `path`, `verified_sha256`, `mapping_reviewed: true`;
- `alignment`: scale_to_mm, rotation_deg, dx_mm, dy_mm, confirmed;
- `mapping`: vier columns (0-basiert in den 15 QM1-Werten, Reihenfolge
  unten X, unten Y, oben X, oben Y), area_factor_to_cm2_m, qr3, evidence,
  axes_rotation_deg;
- optional `boundary_policy`: boundary_tolerance_mm und max_removed_area_mm2.

Es gibt **kein geratenes FRILO-Standardprofil**. Digest und Bestätigung binden
nur das vom Aufrufer überprüfte Profil an eine bestimmte Datei. Sie beweisen
nicht selbst die Richtigkeit der Spaltenbedeutungen.

## Rundungsreste am Rand

Ohne beide expliziten Toleranzparameter wird jeder aus der Decke herausragende
FEM-Bereich abgelehnt. Optional kann eine Zelle auf die Deckenkontur begrenzt
werden, wenn sie vollständig innerhalb des angegebenen Abstandspuffers liegt
und die gesamte entfernte Fläche das gesetzte Limit nicht überschreitet.
Jeder Eingriff wird mit Zell-ID und entfernter Fläche protokolliert. Es werden
keine fehlenden Bereiche ergänzt. Eine Aufteilung der Zelle durch eine Öffnung
wird abgelehnt. Diese Korrektur ist keine automatische Modellanpassung.

## Noch fehlender FRILO-Nachweis und offizieller Vergleichsweg

Die öffentliche Allplan-2026-Hilfe beschreibt den ASF-Import und die Nutzung
als Bewehrungsgrundlage, aber keine QM1/QR3-Spaltentabelle:
https://help.allplan.com/Allplan/2026-0/1033/Allplan/6152.htm

Für einen lokalen Vergleich kann die Originaldatei mit **FEM Datenimport** auf
ein separates Test-Teilbild importiert werden. Die vier beschrifteten
Bewehrungsergebnisse aus FRILO beziehungsweise der Allplan-FEM-Anzeige sowie
Exporteinheiten, FRILO-Modul und Version dienen dann als Referenz für die noch
zu verifizierende Zuordnung. Die Allplan-Anzeige wird vom Plugin nicht heimlich
ausgelesen; hierfür ist kein dokumentierter SDK-Zugriff implementiert.
