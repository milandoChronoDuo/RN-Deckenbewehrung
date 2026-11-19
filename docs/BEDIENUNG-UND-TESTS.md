# Bedienung, Diagnose und lokale Abnahme

Der aktuelle Ablauf in Allplan: **Decke auswählen → Geometrie/UK/OK prüfen →
ASF wählen → Strukturprüfung lesen**.
Matten/Rundstahl lässt sich zur Ansicht umschalten. Erzeugung ist gesperrt.

Der separate Demobefehl liest ausschließlich synthetische JSON-Daten und
schreibt einen Prüfbericht mit As, Kombinationen, Stabkoordinaten und Masse.
`--strategy stahl`, `ausgewogen` oder `verlegeaufwand` wählt die Bewertung.
`rn-asf-inspect` liest reale ALLPLOT-5.0-Dateien strukturell; eine automatische
As-Spaltenzuordnung wird nicht behauptet.

## Lokale Allplan-Integrationstests (noch nicht ausgeführt)

Für jeden Test Allplan-Build, Betriebssystem, verwendete Decke und Ergebnis
mit Screenshot dokumentieren. Nur in einer Kopie eines Testprojekts prüfen.

1. PYP laden, deutsche Beschriftungen und Umschaltung prüfen. Vor Auswahl
   verständlicher Status. Esc darf keine Elemente erzeugen oder verändern.
2. Wand/Stütze anklicken: nicht akzeptiert. Decke beim Überfahren hervorheben.
3. Einschichtige Decke 250 mm: angezeigte Dicke 250 mm. Mehrschichtige Decke:
   Fehlermeldung. Schräge, offene oder verjüngte Decke: Geometrieprüfung muss abbrechen.
   UK/OK an global verschobener Decke prüfen, Öffnungen mit Modell vergleichen.
4. Vorher/nachher Elementanzahl vergleichen: Diagnose darf nichts verändern.
5. NativeElements in einem lokalen SDK-Testskript importieren. Einzelstab
   von (1000,2000,3000) nach (3000,2000,3000), Ø10 erzeugen und prüfen:
   native Bewehrung, Länge 2000 mm, korrekte Achse, keine Haken. Entsprechenden
   Y-Stab prüfen. Diese Fabriken führen selbst keine Schreibvorgänge aus.
6. Bekannten aktiven Mattentyp mit zulässigem Zuschnitt prüfen. Ungültiger
   Typ und übergroßer Zuschnitt müssen scheitern. Native Mattenelemente,
   Z-Lage und übergebene Formate prüfen.
7. Vor produktiver Integration zusätzlich Aussparungsextraktion, UK/OK,
   Layerwahl, Positionskonflikte, Beschriftung/Stahlliste, atomare Erzeugung,
   Fehlerabbruch und Wiederholung verifizieren. Diese Funktionen fehlen noch.

## Fehlerdiagnose

- Python-Script nicht gefunden: PYP-Scriptpfad und Allplan-Suchpfad abgleichen.
- Nicht unterstützte Version: Allplan 2026 erforderlich, keine 2027-Freigabe.
- ImportError NemAll_*: Allplan-Adapter wurde außerhalb von Allplan gestartet.
- ImportError shapely: Rechenkern in seiner virtuellen Umgebung installieren.
- Keine zulässige Kombination: As, verfügbare Kombinationen, Abstand,
  Randabstände, geprüfte Verankerung und maximale Stablänge kontrollieren.
- Koordinaten passen nicht: Exportmaßstab, Modellursprung, Ergebnisachsen und
  Deckenbezug klären; niemals ungeprüft verschieben oder skalieren.

Die automatischen Tests decken reine Python-Funktionen ab. Weder Allplan-
Laufzeit noch Normkonformität sind dadurch nachgewiesen.
