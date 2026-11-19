# ASF-Leser 0.2: beobachteter ALLPLOT-5.0-Dialekt

Die bereitgestellte FRILO-Datei wurde lokal gelesen. Sie enthält 8.757 Knoten,
8.506 Flächenelemente (davon 311 Dreiecke), acht Randkonturen und 8.506 QM1-
Ergebniszeilen mit jeweils 15 Werten. Die Konturen bilden eine Außenkontur und
sieben Öffnungen. Alle Elementpolygone sind gültig; ihre Vereinigung stimmt
mit der Kontur bis auf Rundungsreste der sechs Nachkommastellen überein.
Materialbezeichnungen C_25/30 und B500A sind explizit enthalten. Ein numerischer
Dickenwert 0.2000 ist vorhanden; seine Einheit wird nicht aus dem Wert geraten.

Die Originaldatei und ihre Projektgeometrie sind **nicht** im öffentlichen
Repository enthalten. Tests verwenden ein kleines frei erstelltes Modell mit
klarer Kennzeichnung als synthetisch. Die Originaldatei bleibt ein lokaler
Integrationstest; JSON-Prüfbericht und Geometriebild liegen außerhalb des Repos.

## Gelesene Struktur

- Kopf exakt `5.0 Nemetschek ALLPLOT`, Titel in Folgezeile.
- UTF-8 oder Windows-1252 (deutsche Texte in der Beispieldatei).
- `GL POLY n`: n Koordinatenzeilen mit drei endlichen Zahlen.
- `GP KNOT n`: Knoten-ID und drei Koordinaten.
- `GF ELEM n`: Element-ID, vier Knotenslots, zwei zunächst rohe Kennungen.
  Bei Dreiecken ist der vierte Knotenslot 0. Nur dort ist 0 zulässig.
- `QR3`: 12 numerische Felder, unverändert gespeichert.
- `QM1`: zwei im Beispieldialekt nullwertige Flags, Element-ID, 15 Werte.
- `MATERIAL n`: 12 Felder einschließlich ID, Material- und Stahlbezeichnung.
- `ELEMENT_PROPERTIES n`: ID und drei zunächst rohe Eigenschaftsfelder.
- Andere Datensatztypen werden inventarisiert, **nicht semantisch gelesen**.
  Das betrifft Lasten, Auflager, Verformungen, Schnittgrößen und Balkendaten.

Gezählte Tabellen werden auf Länge, IDs, endliche Werte und vorhandene
Knotenreferenzen geprüft. Die QM1-IDs müssen genau zu den Element-IDs passen.
Unbekannte QM1/QR3-Varianten werden abgewiesen. Der Leser ist kein universeller
ASF-Validator; insbesondere die übersprungenen Erweiterungen sind ungeprüft.

## Noch offene Semantik – keine automatische Freigabe

Aus einer Beispieldatei ist nicht zuverlässig beweisbar, welche der 15 QM1-
Spalten As unten X/Y und oben X/Y bedeuten. Ebenso fehlen die verifizierten
Einheiten-/Achsendefinitionen von QR3 und die Norm-ID-Tabelle. Recherche in den
offiziellen Allplan-2026-PythonParts-Beispielen ergab dafür keine Spezifikation.
Der Dateikopf enthält keine eindeutige FRILO-Modul-/Versionsbezeichnung.

Deshalb liefert `read_asf`/`read_allplot` zunächst ein **AsfModel**, keine für die
Bemessung freigegebenen FEM-Zellen. `ResultMapping` verlangt explizit geprüfte
Spalten, As-Einheitenfaktor, exakten QR3-Bezug, Achsrichtung und Quellenbeleg.
Es existiert kein voreingestelltes FRILO-Mapping. Der Quellenbeleg ist ein
Vertrag mit dem Aufrufer, keine maschinelle Verifikation einer Normquelle.

`asf_cells` prüft vor der Übernahme Maßstab/Rotation/Versatz, horizontales Netz,
Decken- und Öffnungskonturen, Ergebnisachsen und Zellüberlappungen. Es rotiert
keine skalaren As-Werte in andere Richtungen. Elemente außerhalb der echten
Deckenkontur werden abgelehnt, nicht automatisch abgeschnitten. Rundungsreste
an Modellrändern benötigen vor produktivem Einsatz eine explizite, geprüfte
Toleranzstrategie; die jetzige Zellübernahme bleibt dort streng.

Zur endgültigen Zuordnung benötigt wird eine Formatspezifikation von
FRILO/Allplan oder ein überprüfbarer Referenzexport mit beschrifteten vier
As-Ergebnissen, Exporteinheiten, Modul- und Versionsangabe.
