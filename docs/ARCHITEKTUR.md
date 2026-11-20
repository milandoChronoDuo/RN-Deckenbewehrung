# Architektur und Rechenumfang

`src/rn_deckenbewehrung` importiert keine Allplan-Module. Die Adapter unter
`allplan/PythonPartsScripts/RN` benötigen umgekehrt im Diagnosestand weiterhin kein
Shapely. Damit lässt sich die Palette ohne zusätzliche Binärmodule laden.
Vor einer produktiven Verbindung muss Shapely passend zur Allplan-Python-
Version und Windows-Architektur bereitgestellt oder die Geometrie über einen
separaten Prozess angebunden werden.

Maße: mm, Stabquerschnitt cm²/m, Masse kg. Zusammenfassungsabstand als einzige
Benutzereingabe in m; Umrechnung am Eingang. Modellkoordinaten werden erhalten.

Module: `model` Datentypen/Lagen, `geometry` Konturen/Stäbe, `base` wirksame
Grundbewehrung/Mattenkatalog, `fem` Testimport, `regions` Bedarf/Zusammenfassung,
`optimizer` Kandidatenauswahl, `anchorage` Nachweiswerte, `workflow`
Bestätigungssperre, `preview` SVG, `demo` ausführbares Beispiel.

Die FEM-Testzellen decken nicht notwendigerweise die gesamte Decke. Nicht
abgedeckte Flächen sind **unbekannt**, nicht As=0; der Demobericht nennt sie.
Die aktuelle Basisanrechnung ist bewusst konservativ: Nur ein vollständig
von einem wirksamen Nachweisbereich bedecktes Ergebnisfeld erhält Guthaben.
Mattenstoß-Überdeckungen dürfen nicht mehrfach gutgeschrieben werden.

## Optimierung

Harte Bedingungen: As vorhanden ≥ Bedarf; maximaler nomineller Abstand;
minimaler tatsächlicher lichter Abstand nach Reihenaufteilung; positive
prüfbelegte Verankerung je Durchmesser; alle verlängerten Stabachsen innerhalb
der für den Durchmesser erodierten Deckenkontur; Stablänge ≤ Vorgabe.
Die Abstandswerte sind explizite Projektgrenzen, keine automatisch abgeleiteten
Normwerte. Globale Lagenkollisionen bleiben außerhalb dieses Moduls.

Für jeden Bereich wird jede freigegebene Kombination geprüft. Zielwert:

`Masse [kg] + w_Stab × Stabanzahl + w_Typ × neuer Kombinationstyp`

| Strategie | w_Stab [kg-Äquivalent] | w_Typ [kg-Äquivalent] |
|---|---:|---:|
| Geringste Stahlmenge | 0 | 0 |
| Ausgewogen | 0,15 | 3 |
| Geringster Verlegeaufwand | 2 | 30 |

Die Masse beinhaltet beide Endverlängerungen. Automatische Stöße werden nicht
angenommen. Deterministische Greedy-Auswahl nach absteigendem As-Bedarf;
keine Behauptung eines globalen Optimums. Kein festes Limit für Positionstypen.
Zusammenfassung ist vorgelagert: Abstand, maximale Ausdehnung, Zusatzfläche,
Öffnungen und Überschneidung mit anderen Bereichen begrenzen sie. Der Proxy
`Fläche × As` bewertet Kandidaten, ersetzt aber keinen Vergleich vollständiger
Verlegepläne. Eine gemeinsame globale Optimierung beider Schritte fehlt.

## Ergänzung 0.2

`asf` und `solid` sind Standardbibliotheksmodule und werden mit `model`
reproduzierbar für Allplan gebündelt (`tools/bundle_runtime.py`). Tests prüfen
Quellgleichheit. `alignment` und `planning` nutzen Shapely und bleiben im
externen Rechenkern. Einzelne Module lassen sich später an Allplan 2027
anpassen, ohne die Berechnungen zu verändern.

## Ergänzung 0.3

`assessment` verbindet räumlich indizierte Ergebnisprüfung und konservative
Rechteckbildung mit dem Optimierer. `import_quality` übernimmt ausschließlich
explizit erlaubte, protokollierte Randkorrekturen. `review_report` und
`review_cli` liefern einen reproduzierbaren, weiterhin nicht produktiv
freigegebenen Gesamtprüflauf. Keine Änderungen an der Allplan-Schreibgrenze.
