# MASTER-PROMPT: RN Deckenbewehrung – Intelligentes PythonPart für Allplan 2026

## 1. Deine Rolle und dein Auftrag

Du bist ein erfahrener Allplan-PythonParts-Entwickler, Tragwerksplaner, Stahlbeton-Konstrukteur, Python-Softwarearchitekt sowie UI/UX-Designer.

Entwickle ein vollständiges, professionelles und möglichst robustes Plugin namens **RN Deckenbewehrung** für Allplan 2026. Die spätere Kompatibilität mit Allplan 2027 soll durch eine saubere Architektur vorbereitet werden.

Das Ziel ist ein Allplan-PythonPart, mit dem ich eine vorhandene Stahlbetondecke auswählen, eine Grundbewehrung in Matten oder Rundstahl definieren, eine ASF-Datei aus einer FEM-Berechnung einlesen und daraus automatisch konstruktiv sinnvolle Zulagebewehrungen erzeugen kann.

Die Anwendung soll insbesondere für die praktische Erstellung von Bewehrungsplänen im Ingenieurbüro geeignet sein.

**Zentrale Entwicklungsziele:**

- Sehr einfache und intuitive Bedienung.
- Wenige Eingaben und übersichtliche Eigenschaftenpalette.
- Keine unnötigen Dialoge oder überladenen Einstellungen.
- Vollständig getrennte Einstellungen für Matten und Rundstahl.
- Direkte Auswahl einer Decke im Allplan-Modell.
- Automatische Auswertung einer ASF-Datei.
- Optimierte Grund- und Zulagebewehrung.
- Möglichst wenige, gut verlegbare Zulagebereiche.
- Automatische Berücksichtigung von Aussparungen.
- Nachvollziehbare Berechnung von Verankerungen und Übergreifungen.
- Native Allplan-Bewehrung anstatt rein grafischer Ersatzobjekte.
- Trennung der oberen und unteren Bewehrung auf eigenen Layern.
- Professionelle Icons und verständliche grafische Hilfen.
- GitHub-Versionierung und einfache Installation.

Erzeuge tatsächlich lauffähige Projektdateien, keine Pseudocode-Sammlung. Teile den Code bei Bedarf in sinnvoll getrennte Module auf.

Verwende ausschließlich dokumentierte, für Allplan 2026 geeignete API-Funktionen.

---

## 2. Technische Grundlagen

Verwende vorrangig folgende offizielle Quellen:

- Allplan Python API 2026:
  https://pythonparts.allplan.com/2026/
- Allplan PythonParts Examples:
  https://github.com/NemetschekAllplan/PythonPartsExamples
- Allplan 2026 Onlinehilfe:
  https://help.allplan.com/

Untersuche insbesondere:

- PythonPart Script Objects und Interactors.
- Elementauswahl und Elementfilter.
- Architekturbauteile und deren Geometrien.
- Rundstahl-Biegeformen und Verlegungen.
- Mattenbewehrung und Mattenverlegungen.
- Layer- und Formatzuweisung.
- Benutzerdefinierte Eigenschaftenpaletten.
- Geometrische Operationen und Polygonbearbeitung.
- Elementerzeugung und Transaktionen.
- Plugin-Manager und Installationsmöglichkeiten.

Prüfe vor jeder Verwendung einer Allplan-API-Klasse deren tatsächliche Existenz, Signatur und Eignung für Allplan 2026 anhand der Dokumentation oder des installierten SDK.

Falls eine Funktion nicht dokumentiert oder nicht zugänglich ist, recherchiere eine funktionierende Alternative. Erfinde niemals Klassen, Methoden oder Rückgabeformate.

**Entwicklungsarchitektur:**

Verwende einen Interactor-basierten Workflow, soweit für die Auswahl und grafische Bearbeitung erforderlich, und eine modular aufgebaute Python-Anwendung.

Die eigentliche Optimierungslogik soll weitestgehend unabhängig von der Allplan API funktionieren, damit sie mit automatisierten Unit-Tests überprüft werden kann.

Alle Maße und Einheiten müssen konsistent behandelt werden.

---

## 3. Schritt 1 – Decke auswählen

Beim Start des Plugins soll der Benutzer aufgefordert werden, eine Stahlbetondecke im Allplan-Modell auszuwählen.

Anforderungen:

- Direkte Auswahl durch Anklicken.
- Geeignete Bauteile beim Überfahren mit der Maus hervorheben.
- Ausschließlich geeignete Deckenbauteile akzeptieren.
- Optional mehrere zusammenhängende Deckenbauteile auswählen.
- Geometrie und vorhandene Aussparungen erkennen.
- Konturen einschließlich konkaver Bereiche berücksichtigen.
- Oberkante, Unterkante und Deckenstärke auslesen.
- Die Lage der Decke im Allplan-Koordinatensystem beibehalten.
- Prüfen, ob die ausgewählte Geometrie für die Flächenbewehrung geeignet ist.

Falls mehrere Decken ausgewählt wurden, muss die Software prüfen, ob sie geometrisch sinnvoll zu einer gemeinsamen Bewehrungsfläche verarbeitet werden können.

Geometrisch oder konstruktiv nicht geeignete Bereiche dürfen nicht stillschweigend zusammengeführt werden.

Im ersten Entwicklungsstand kann die automatische Bewehrung auf ebene Decken mit konstanter Dicke beschränkt werden. Nicht unterstützte Geometrien sollen eine verständliche Fehlermeldung erzeugen.

---

## 4. Schritt 2 – Allgemeine Bemessungsparameter

Nach der Deckenauswahl sollen die folgenden Angaben in der Eigenschaftenpalette erscheinen:

- Erkannte Deckenstärke, möglichst automatisch übernommen.
- Betonfestigkeitsklasse, aus Bauteilattributen übernommen, sofern zuverlässig vorhanden.
- Betonstahlgüte beziehungsweise geeigneter Bewehrungsstahlkatalog.
- Obere Betondeckung.
- Untere Betondeckung.
- Seitliche Betondeckung beziehungsweise Randbedingungen.
- Anzuwendendes Normenwerk und Nationaler Anhang.
- Verankerungs- und Übergreifungsparameter.
- Verbundbedingungen.

Die Deckenstärke und Betonfestigkeit sollen automatisch eingelesen werden, soweit verfügbar. Eine manuelle Korrektur muss möglich sein.

Die Verbundbedingungen müssen entsprechend den maßgebenden Bemessungsregeln bestimmt werden. Dabei sind insbesondere Bauteillage, Betonierbedingungen, Höhenlage der Stäbe im Bauteil und weitere relevante Parameter zu berücksichtigen.

Eine automatische Zuordnung allein anhand der Betondeckung ist nicht ausreichend.

Verwende konservative und nachvollziehbare Voreinstellungen, aber erzeuge bei unvollständigen Angaben keine unbelegten Bemessungswerte.

---

## 5. Schritt 3 – Grundbewehrungsart wählen

Der Benutzer erhält eine zentrale Auswahl:

**Grundbewehrung als:**

1. Mattenbewehrung
2. Rundstahlbewehrung

Je nach Auswahl soll sich die gesamte Eingabemaske automatisch ändern.

Es dürfen ausschließlich die für die gewählte Bewehrungsart relevanten Parameter angezeigt werden.

Die Bedienung soll möglichst kompakt und verständlich bleiben.

### 5.1 Mattenbewehrung

Erstelle folgende Einstellungen:

**Untere Mattenbewehrung:**

- Mattentyp über Allplan-Mattenkatalog auswählen.
- Auswahl „Keine Matte“ ermöglichen.

**Obere Mattenbewehrung:**

- Mattentyp über Allplan-Mattenkatalog auswählen.
- Auswahl „Keine Matte“ ermöglichen.

**Allgemeine Matteneinstellungen:**

- Längsübergreifung.
- Querübergreifung.
- Obere und untere Betondeckung.
- Mattenausrichtung beziehungsweise Drehwinkel, falls erforderlich.
- Automatische Anpassung an die Deckenfläche.
- Aussparungen berücksichtigen.
- Zuschnitt und Mattenstöße berücksichtigen.

Die Übergreifungslängen sollen möglichst normgerecht vorgeschlagen werden, aber manuell einstellbar sein.

Das System darf keine Matten verwenden, die im aktiven Allplan-Mattenkatalog nicht vorhanden sind.

Berücksichtige, dass Matten je nach Typ unterschiedliche Bewehrungsquerschnitte in Längs- und Querrichtung besitzen können.

Matten dürfen nicht einfach durch eine gleichmäßig eingefärbte Fläche simuliert werden. Sie müssen als native Allplan-Mattenbewehrung erzeugt werden.

Sind oben oder unten „Keine Matte“ ausgewählt, darf in dieser Lage keine Grundmattenbewehrung erzeugt werden.

### 5.2 Rundstahlbewehrung

Erstelle getrennte Eingaben für vier mögliche Grundbewehrungslagen.

**Untere Bewehrung:**

1. Lage unten:
- Aktivieren/deaktivieren.
- Stabdurchmesser.
- Stababstand.
- Verlegerichtung X oder Y.
- Übergreifungslänge beziehungsweise automatische Berechnung.

2. Lage unten:
- Aktivieren/deaktivieren.
- Stabdurchmesser.
- Stababstand.
- Verlegerichtung automatisch senkrecht zur ersten Lage.
- Eigene Übergreifungslänge beziehungsweise automatische Berechnung.

**Obere Bewehrung:**

1. Lage oben:
- Aktivieren/deaktivieren.
- Stabdurchmesser.
- Stababstand.
- Verlegerichtung X oder Y.
- Übergreifungslänge beziehungsweise automatische Berechnung.

2. Lage oben:
- Aktivieren/deaktivieren.
- Stabdurchmesser.
- Stababstand.
- Verlegerichtung automatisch senkrecht zur ersten Lage.
- Eigene Übergreifungslänge beziehungsweise automatische Berechnung.

**Wichtige Definition der Lagen:**

- Die 1. Lage unten ist die unterste Bewehrungslage unmittelbar oberhalb der unteren Betondeckung.
- Die 2. Lage unten liegt darüber.
- Die 1. Lage oben ist die oberste Bewehrungslage unmittelbar unterhalb der oberen Betondeckung.
- Die 2. Lage oben liegt darunter.

Das PythonPart muss die tatsächlichen Stabachsen und Höhenlagen anhand von Betondeckung und Stabdurchmesser berechnen.

Jede der vier Lagen muss unabhängig aktivierbar oder deaktivierbar sein.

Es muss möglich sein, nur eine einzelne Lage zu erzeugen oder sogar vollständig auf Grundbewehrung zu verzichten.

Wenn die erste Lage deaktiviert wird, darf die verbleibende zweite Lage nicht aufgrund einer starren Nummerierung unnötig weit von der Betonoberfläche entfernt liegen. Die tatsächliche Schichtung ist geometrisch korrekt neu anzuordnen, während die eingestellte Verlegerichtung erhalten bleibt.

Deaktivierte Lagen dürfen keinen Bewehrungsquerschnitt zur FEM-Abdeckung beitragen.

---

## 6. Schritt 4 – ASF-Datei einlesen

Der Benutzer wählt eine ASF-Datei aus der FEM-Berechnung.

Ziel ist die möglichst einfache automatische Auswertung der erforderlichen Deckenbewehrung.

**Bevorzugte Lösung:**

Ein eigenständiger ASF-Reader, der die Datei direkt einliest.

Untersuche zuerst das tatsächliche Dateiformat anhand einer repräsentativen Beispieldatei. Prüfe insbesondere Datenstruktur, Ergebnisarten, Einheiten, Koordinatensystem, Bewehrungsrichtungen sowie Kennzeichnung von oberen und unteren Bewehrungsergebnissen.

Falls ein direktes, verlässliches Einlesen ohne hinreichend dokumentierte Datenstruktur nicht möglich ist, untersuche den offiziellen Allplan-FEM-Datenimport als Alternative.

Implementiere keinen fiktiven ASF-Parser.

Sollte eine echte Datei für die Entwicklung fehlen, erstelle zunächst eine klar getrennte Testdaten-Schnittstelle und kennzeichne die ASF-Anbindung als noch nicht implementiert.

**Erforderliche Ergebnisdaten:**

- Untere Bewehrung X.
- Untere Bewehrung Y.
- Obere Bewehrung X.
- Obere Bewehrung Y.
- Räumliche Zuordnung der FEM-Ergebnisse.
- Erforderliche Bewehrungsflächen in cm²/m beziehungsweise zuverlässig umgerechneten Einheiten.

Die ASF-Daten müssen mit der Deckengeometrie abgeglichen werden.

Prüfe:

- Koordinatenversatz.
- Rotation.
- Maßstab.
- FEM-Modellgrenzen.
- Deckenaussparungen.
- Fehlende Ergebniswerte.
- Nicht übereinstimmende Ergebnisrichtungen.

Ein Koordinatenabgleich darf nicht ohne Kontrolle automatisch angenommen werden.

Stelle die FEM-Ergebnisse als farbige Vorschau im Grundriss dar.

Der Benutzer soll zwischen den vier Ergebnisrichtungen umschalten können.

---

## 7. Schritt 5 – Grundbewehrung erstellen und auswerten

Berechne zunächst die tatsächlich vorhandene Bewehrungsfläche der gewählten Grundbewehrung.

Berücksichtige:

- Mattenbewehrung oder Rundstahlbewehrung.
- Tatsächliche Stabdurchmesser und Stababstände.
- Mattenquerschnitte in den jeweiligen Richtungen.
- Aktivierte beziehungsweise deaktivierte Lagen.
- Aussparungen.
- Mattenstöße und erforderliche Übergreifungen.
- Randbereiche und Stabenden.
- Tatsächliche Lage und Richtung der Bewehrung.

Die Grundbewehrung soll zunächst in einer Vorschau erscheinen.

Anschließend kann der Benutzer die Grundbewehrung erzeugen oder gemeinsam mit den Zulagen endgültig erzeugen lassen.

Bei der Berechnung der Zulagen darf nur die im jeweiligen Bereich tatsächlich wirksame Grundbewehrung angerechnet werden.

---

## 8. Schritt 6 – Zusätzlich erforderliche Bewehrung bestimmen

Für jedes FEM-Ergebnisfeld wird der zusätzliche Bedarf ermittelt.

Grundprinzip:

As,Zulage = max(0; As,erforderlich − As,vorhanden)

Diese Berechnung erfolgt getrennt für:

- Unten X.
- Unten Y.
- Oben X.
- Oben Y.

Dabei muss die Software beachten, dass der rechnerische Bewehrungsquerschnitt allein noch keinen vollständigen konstruktiven Nachweis darstellt.

Die zusätzlich erforderlichen Bewehrungsbereiche sollen aus den FEM-Daten geometrisch erzeugt werden.

Kleine Einzelbereiche sollen nicht automatisch in zahlreiche kleinteilige Bewehrungspositionen umgesetzt werden.

Stattdessen erfolgt anschließend eine Optimierung der Zulagebereiche.

---

## 9. Schritt 7 – Zulagebereiche zusammenfassen

Der Benutzer soll einen Zusammenfassungsabstand in Metern eingeben können.

Beispiel:

**Zulagebereiche zusammenfassen, wenn Abstand kleiner/gleich 2,00 m.**

Die Software untersucht dabei die aus den FEM-Daten ermittelten Zulageflächen.

Anforderungen:

- Abstand geometrisch korrekt ermitteln.
- Nur Bereiche derselben oberen/unteren Lage und Bewehrungsrichtung vergleichen.
- Benachbarte Zulagebereiche als Zusammenfassungskandidaten betrachten.
- Aussparungen und Deckenränder berücksichtigen.
- Keine unzulässigen Verlegungen über Öffnungen erzeugen.
- Zusätzliche Stahlmengen beim Zusammenfassen berücksichtigen.
- Lange Ketten von Zulagebereichen nicht automatisch unbegrenzt vereinigen.
- Möglichst rechteckige und gut verlegbare Zulageflächen erzeugen.
- Unnötige kleinflächige Bewehrungsbereiche vermeiden.

Der eingestellte Abstand ist eine Bedingung zur Prüfung möglicher Zusammenfassungen, nicht automatisch eine Verpflichtung zur Zusammenfassung.

Die resultierenden Zulagebereiche sollen grafisch dargestellt werden.

Der Benutzer soll den Zusammenfassungsabstand verändern und eine neue Vorschau berechnen lassen können.

---

## 10. Schritt 8 – Zulagebewehrung automatisch optimieren

Dies ist eine der wichtigsten Funktionen der gesamten Anwendung.

Das PythonPart soll automatisch entscheiden, welche Stabdurchmesser und Stababstände für die einzelnen Zulagen wirtschaftlich und konstruktiv sinnvoll sind.

Beispiele:

- Ø8/10
- Ø10/15
- Ø12/20
- Ø12/15
- Ø14/20
- weitere zulässige Kombinationen

Diese Werte dienen nur als Beispiele.

Der Algorithmus soll alle freigegebenen Kombinationen prüfen.

**Wichtig:**

Es darf keinen global erzwungenen Durchmesser und keinen global erzwungenen Stababstand für alle Zulagen geben.

Jeder Bereich soll entsprechend seinem erforderlichen Bewehrungsbedarf eine geeignete Kombination erhalten.

Dabei soll das PythonPart nach Möglichkeit unterschiedliche Zulagebereiche vereinheitlichen, wenn dies wirtschaftlich und konstruktiv sinnvoll ist.

### Optimierungsstrategie

Der Benutzer kann zwischen drei Strategien wählen:

1. **Geringste Stahlmenge**
   - Möglichst niedriger Gesamtstahlverbrauch.
   - Mehr unterschiedliche Zulagekombinationen zulässig.

2. **Ausgewogen – Standardeinstellung**
   - Wirtschaftliche Stahlmenge.
   - Sinnvolle Standarddurchmesser und Abstände.
   - Möglichst wenige unterschiedliche Bewehrungskombinationen.

3. **Geringster Verlegeaufwand**
   - Möglichst einfache Ausführung.
   - Größere, zusammenhängende Zulagebereiche bevorzugen.
   - Möglichst wenige unterschiedliche Kombinationen und Verlegevorgänge.

Die Optimierung soll nicht nur die Querschnittsfläche, sondern auch die gesamte benötigte Stahlmenge einschließlich konstruktiv erforderlicher Stabverlängerungen berücksichtigen.

Jede vorgeschlagene Kombination muss vorher alle zwingenden Bedingungen erfüllen.

Berücksichtige:

- Ausreichende Bewehrungsfläche.
- Zulässige Stababstände.
- Verankerungslängen.
- Übergreifungslängen.
- Einbaubarkeit.
- Lage der übrigen Bewehrung.
- Öffnungen und Randbedingungen.
- Maximale wirtschaftlich oder technisch zulässige Stablängen.
- Anzahl unterschiedlicher Bewehrungspositionen.
- Zusätzliche Stahlmengen durch Bereichszusammenfassung.

Die drei Optimierungsstrategien müssen zu nachvollziehbar unterschiedlichen Bewertungen führen können.

Definiere hierzu eine transparente, dokumentierte Optimierungsfunktion mit harten Zulässigkeitsbedingungen und gewichteten Optimierungskriterien.

Es soll keine Benutzereinstellung geben, die eine feste maximale Anzahl von Zulagepositionstypen erzwingt.

---

## 11. Schritt 9 – Automatische Verankerungen und Übergreifungen

Berechne erforderliche Verankerungs- und Übergreifungslängen auf Grundlage der ausgewählten Bemessungsregeln.

Berücksichtige insbesondere:

- Betonfestigkeitsklasse.
- Betonstahlgüte.
- Stabdurchmesser.
- Betondeckung.
- Verbundbedingungen.
- Stablage.
- Tatsächliche Beanspruchung, soweit nachweisbar.
- Verankerungsart.
- Erforderliche konstruktive Zusatzbedingungen.
- Anteil gestoßener Stäbe und sonstige relevante Parameter.

Wenn für eine korrekte Berechnung wesentliche Angaben fehlen, muss die Anwendung diese anfordern oder den betroffenen Bereich als prüfpflichtig kennzeichnen.

Verwende keine pauschale 40-d- oder 50-d-Regel als vermeintlich allgemeinen normgerechten Nachweis.

Berechne getrennt:

- Verankerung der Grundbewehrung.
- Übergreifung der Grundbewehrung.
- Verankerung der Zulagebewehrung.
- Übergreifung von Zulagen.

Verlängere Stäbe nur so, dass sie innerhalb der zulässigen Bauteilgeometrie und konstruktiven Randbedingungen angeordnet werden können.

Wenn eine erforderliche Verankerung nicht möglich ist, muss die Anwendung eine eindeutige Fehlermeldung ausgeben.

Die notwendigen Stablängen müssen grafisch und im Prüfbericht nachvollziehbar sein.

---

## 12. Schritt 10 – Aussparungen und geometrische Sonderfälle

Aussparungen müssen bei Grundbewehrung und Zulagen automatisch berücksichtigt werden.

Anforderungen:

- Alle tatsächlichen Öffnungskonturen erfassen.
- Keine Bewehrungsstäbe durch Aussparungen führen.
- Betondeckung an Öffnungsrändern einhalten.
- Unterbrochene Bewehrungsreihen korrekt behandeln.
- Erforderliche Verankerungen an Öffnungen prüfen.
- Öffnungsrand- und Eckbewehrungen als gesonderte konstruktive Aufgabe behandeln.
- Zusätzliche Bewehrung aus der FEM-Auswertung nicht ohne Prüfung als vollständige Öffnungsbewehrung ansehen.

Rechteckige, polygonale und geeignete kreisförmige Öffnungen sollen berücksichtigt werden.

Bei Sonderfällen, die sich nicht zuverlässig automatisch lösen lassen, muss die Anwendung die Stelle markieren und eine manuelle Prüfung verlangen.

---

## 13. Schritt 11 – Interaktive Vorschau und Bearbeitung

Vor der endgültigen Erstellung der Zulagen soll eine grafische Vorschau erscheinen.

Darstellung:

- Grundbewehrung.
- Zulagebereiche.
- Obere Bewehrung.
- Untere Bewehrung.
- Bewehrungsrichtungen X/Y.
- Erforderliche Bewehrungsflächen.
- Tatsächlich vorgesehene Bewehrungsflächen.

Unterscheide die Bereiche durch gut erkennbare Farben, Linien oder Schraffuren.

Der Benutzer soll Zulagebereiche direkt im Grundriss auswählen können.

Beim Anklicken eines Bereichs werden die jeweiligen Einstellungen in der Palette angezeigt.

Bearbeitungsmöglichkeiten:

- Durchmesser ändern.
- Stababstand ändern.
- Zulagebereich verschieben.
- Zulagebereich vergrößern oder verkleinern.
- Zulagebereich teilen.
- Zwei geeignete Bereiche zusammenfassen.
- Zulage löschen.
- Neue Zulage manuell ergänzen.

Nach jeder manuellen Änderung soll eine erneute Prüfung der betroffenen Bewehrung möglich sein.

Die endgültige Erzeugung muss eine klare Bestätigung erfordern.

---

## 14. Schritt 12 – Native Allplan-Bewehrung erzeugen

Die erzeugte Bewehrung muss als tatsächliche Allplan-Bewehrung verfügbar sein.

Keine Ersatzdarstellung durch einfache Linien, Polygone oder unverbundene 3D-Zylinder.

Verwende native:

- Rundstahl-Biegeformen.
- Rundstahlverlegungen.
- Mattenbewehrungselemente.
- Bewehrungspositionen.
- Geeignete Allplan-Attribute und Formatparameter.

Die Bewehrung muss in den regulären Ansichten und Schnitten nutzbar sein.

Sie soll mit den vorhandenen Allplan-Funktionen für Bewehrungsbeschriftung und Stahllisten grundsätzlich weiterverarbeitet werden können.

**Layerzuordnung:**

- Sämtliche untere Grundbewehrung und unteren Zulagen auf den Layer für untere Bewehrung.
- Sämtliche obere Grundbewehrung und oberen Zulagen auf den Layer für obere Bewehrung.

Ermögliche die Auswahl der tatsächlichen Allplan-Layer in den Einstellungen.

Verwende keine ungeprüften, fest codierten Layer-IDs.

Wenn für einen Layer keine zuverlässige Zuordnung möglich ist, fordere den Benutzer zur Auswahl auf.

Berücksichtige die korrekte Positionsnummerierung und vermeide doppelt erzeugte Elemente.

Das Plugin darf keine fremde, bereits vorhandene Bewehrung oder andere Allplan-Elemente verändern oder löschen.

---

## 15. Vereinfachtes Änderungsverhalten für Version 1

Für die erste Version wird bewusst auf komplexe automatische Änderungsverfolgung verzichtet.

Nicht implementieren:

- Automatische Aktualisierung bei jeder Änderung der Deckengeometrie.
- Automatische Synchronisierung geänderter ASF-Dateien.
- Komplexe Versionshistorien.
- Automatisches Nachführen manuell bearbeiteter Bewehrung.

Stattdessen gilt:

Wenn sich die Deckengeometrie oder Berechnungsgrundlage wesentlich verändert, kann der Benutzer die durch das Plugin erzeugte Bewehrung entfernen und vollständig neu erzeugen.

Das Plugin soll trotzdem:

- Den Erzeugungsvorgang eindeutig einer bestimmten Decke zuordnen.
- Die eigenen erzeugten Elemente identifizieren können.
- Ein sicheres Entfernen ausschließlich der selbst erzeugten Elemente unterstützen, soweit dies mit der dokumentierten API zuverlässig möglich ist.
- Fremde Bewehrung erhalten.
- Vor einem erneuten Erzeugen vor möglichen Doppelverlegungen warnen.

Ohne sichere Identifikation darf keine automatische Löschung erfolgen.

---

## 16. UI/UX-Design

Erstelle eine hochwertige, konsistente und funktionale Benutzeroberfläche innerhalb der Möglichkeiten der Allplan-2026-PythonParts-Palette.

Die Benutzeroberfläche soll sich an professioneller CAD-Software orientieren.

**Geplanter Ablauf:**

1. Decke auswählen.
2. Allgemeine Parameter prüfen.
3. Matten oder Rundstahl wählen.
4. Grundbewehrung definieren.
5. ASF-Datei laden.
6. Zusammenfassungsabstand festlegen.
7. Optimierungsstrategie auswählen.
8. Vorschau berechnen.
9. Zulagen prüfen oder anpassen.
10. Bewehrung erzeugen.

Gestaltungsanforderungen:

- Klare Gruppierung der Parameter.
- Keine überflüssigen Eingabefelder.
- Sinnvolle Standardwerte.
- Automatische Übernahme vorhandener Bauteilinformationen.
- Übersichtliche Dropdowns.
- Verständliche Beschriftungen in deutscher Sprache.
- Eingaben mit sichtbaren Einheiten.
- Tooltips für komplexe Funktionen.
- Konsistente Icons.
- Deutliche Statusmeldungen.
- Verständliche Fehlermeldungen.
- Visuelles Feedback bei der Bauteilauswahl.
- Verhindern ungültiger Eingaben.
- Gut erkennbare Schaltflächen für Vorschau und endgültige Erzeugung.

Die Bedienung soll für einen Tragwerksplaner ohne Programmierkenntnisse verständlich sein.

### Icons und Bilder

Entwickle passende eigene Icons und erklärende Grafiken für:

- Decke auswählen.
- Mattenbewehrung.
- Rundstahlbewehrung.
- Obere Bewehrung.
- Untere Bewehrung.
- ASF-Import.
- Grundbewehrung.
- Zulagebewehrung.
- Zulagen zusammenfassen.
- Stahlmenge optimieren.
- Verlegeaufwand optimieren.
- Verankerung.
- Aussparung.
- Vorschau.
- Bewehrung erzeugen.
- Prüfhinweise und Fehlermeldungen.

Erstelle die Assets nach Möglichkeit als SVG-Quelldateien und, falls Allplan es erfordert, in den tatsächlich unterstützten Bildformaten.

Prüfe die Allplan-Vorgaben für Icongrößen, Dateiformate und Einbindung.

Erzeuge außerdem verständliche Schemazeichnungen beziehungsweise Hilfebilder zu:

- Reihenfolge der oberen und unteren Rundstahllagen.
- Mattenübergreifung längs und quer.
- Zulagebereichen und Zusammenfassungsabstand.
- Verankerungen.
- Aussparungen und unterbrochener Bewehrung.
- FEM-Bewehrungsbedarf im Vergleich zur tatsächlich vorgesehenen Bewehrung.

Falls die verwendete Entwicklungsumgebung keine Bildgenerierung unterstützt, erstelle die Grafiken programmatisch als SVG und dokumentiere die Einbindung.

Gestalte diese Grafiken als technische Vektorillustrationen, nicht als dekorative Stockbilder.

---

## 17. Softwarearchitektur und Projektstruktur

Entwickle eine saubere, modular aufgebaute Ordnerstruktur.

Trenne mindestens folgende Verantwortlichkeiten:

- Plugin-Einstiegspunkt und Allplan-Integration.
- Auswahl und Auswertung der Deckengeometrie.
- ASF-Import und Validierung.
- Geometrische Verarbeitung.
- Mattenbewehrung.
- Rundstahlbewehrung.
- Grundbewehrungsberechnung.
- Zulagebereichsermittlung.
- Zulagezusammenfassung.
- Zulagenoptimierung.
- Verankerungs- und Übergreifungsberechnung.
- Allplan-Bewehrungserzeugung.
- Layer- und Positionsverwaltung.
- Benutzeroberfläche.
- Icons und Grafiken.
- Fehlerbehandlung.
- Tests und Testdaten.

Vermeide eine einzige große Python-Datei.

Verwende nachvollziehbare Namen, dokumentierte Schnittstellen und geeignete Datentypen.

Verhindere zyklische Abhängigkeiten.

Isoliere die direkte Allplan-API-Anbindung von der reinen Rechen- und Optimierungslogik.

---

## 18. Fehlerbehandlung und technische Sicherheit

Implementiere systematische Validierungen.

Prüfe insbesondere:

- Keine Decke ausgewählt.
- Ungültige Deckengeometrie.
- Nicht unterstützte Geometrie.
- Fehlende Betonfestigkeit.
- Ungültige Betondeckung.
- Unzulässige Durchmesser und Abstände.
- Fehlende Mattentypen.
- ASF-Datei nicht lesbar.
- ASF-Datei passt nicht zur Decke.
- Ergebnisrichtungen nicht eindeutig.
- Nicht ausreichende Bewehrung.
- Nicht realisierbare Verankerungen.
- Überlappende oder doppelte Bewehrung.
- Bewehrung innerhalb von Aussparungen.
- Fehlende Allplan-Layer.
- Nicht unterstützte Allplan-API-Funktionen.

Bei Fehlern darf das Plugin nicht stillschweigend unvollständige oder falsche Bewehrung als erfolgreich erzeugt kennzeichnen.

Fehler sollen möglichst vor der endgültigen Elementerzeugung erkannt werden.

Verwende Transaktionen beziehungsweise geeignete Sicherheitsmechanismen, um teilweise erfolgte Erzeugungen zuverlässig zu behandeln.

---

## 19. Tests und Qualitätssicherung

Erstelle automatisierte Tests für alle reinen Python-Module.

Mindestens folgende Testfälle:

1. Einfache rechteckige Decke.
2. Decke mit einer rechteckigen Öffnung.
3. Decke mit mehreren Öffnungen.
4. Polygonale Decke.
5. Mattenbewehrung oben und unten.
6. Nur untere Mattenbewehrung.
7. Nur obere Mattenbewehrung.
8. Keine Grundbewehrung.
9. Rundstahl mit vier aktiven Lagen.
10. Rundstahl mit einzelnen deaktivierten Lagen.
11. Unterschiedliche Verlegerichtungen.
12. Zulagebedarf kleiner als Grundbewehrung.
13. Zulagebedarf größer als Grundbewehrung.
14. Zulagebereiche mit weniger als 2 m Abstand.
15. Zulagebereiche mit mehr als 2 m Abstand.
16. Unterschiedliche Optimierungsstrategien.
17. Nicht ausreichende verfügbare Stabdurchmesser.
18. Fehlende Verankerungsparameter.
19. Nicht übereinstimmende ASF-Koordinaten.
20. Sicheres erneutes Erzeugen ohne Doppelbewehrung.

Erstelle darüber hinaus Allplan-spezifische Integrationstests, die ich lokal in Allplan 2026 durchführen kann.

Führe alle Tests aus, die in der verfügbaren Entwicklungsumgebung tatsächlich ausführbar sind.

Unterscheide klar zwischen:

- Automatisch getesteten Funktionen.
- Dokumentierten, aber noch nicht in Allplan getesteten Funktionen.
- Noch nicht implementierten Funktionen.

Behaupte niemals, dass das Plugin vollständig getestet oder fehlerfrei sei, wenn keine entsprechenden Nachweise vorliegen.

---

## 20. Installation und Bereitstellung

Das Plugin soll sich möglichst einfach in Allplan 2026 installieren lassen.

Prüfe bevorzugt die Bereitstellung über den integrierten Allplan Plugin-Manager.

Erstelle alle notwendigen Dateien für ein geeignetes Installationspaket, soweit das offizielle SDK dies unterstützt.

Zusätzlich soll eine manuelle Installation möglich sein.

Erstelle:

- Vollständigen Quellcode.
- Alle erforderlichen PYP-Dateien.
- Notwendige Konfigurationsdateien.
- Icons und Hilfsgrafiken.
- README.md.
- Installationsanleitung.
- Bedienungsanleitung auf Deutsch.
- Anleitung zur Fehlerdiagnose.
- Beispieldaten und Testanweisungen.
- Versionsinformationen.
- Anforderungen und unterstützte Allplan-Versionen.

Arbeite GitHub-kompatibel.

Falls das Repository bereits eine AGENTS.md, Installationskonfiguration oder GitHub Actions enthält, prüfe und berücksichtige diese.

Nutze vorhandene sinnvolle Projektkonventionen und überschreibe keine funktionierenden bestehenden Komponenten ohne Notwendigkeit.

---

## 21. Vorgehensweise bei der Implementierung

Arbeite selbstständig und systematisch.

1. Recherchiere die benötigten Allplan-2026-Funktionen.
2. Prüfe relevante offizielle Codebeispiele.
3. Erstelle eine technische Architektur.
4. Implementiere zuerst Deckenauswahl, einfache Rundstahl- und Mattenverlegung sowie die dazugehörigen Oberflächen.
5. Untersuche und implementiere die ASF-Anbindung anhand verifizierter Dateidaten.
6. Implementiere die Grundbewehrungsberechnung.
7. Entwickle die Zulagebereichslogik.
8. Entwickle den Optimierungsalgorithmus.
9. Implementiere die Verankerungs- und Übergreifungsberechnung auf Grundlage verifizierter Bemessungsregeln.
10. Verbinde die Berechnungen mit der nativen Allplan-Bewehrungserzeugung.
11. Erstelle die Icons, Grafiken und Hilfetexte.
12. Implementiere Fehlerbehandlung und Tests.
13. Erstelle Installation und Dokumentation.
14. Prüfe abschließend die Abhängigkeiten und die Vollständigkeit aller Dateien.

**Wichtige Arbeitsregel:**

Implementiere keine nicht verifizierten Bemessungsformeln oder Allplan-API-Aufrufe.

Falls notwendige technische Informationen oder eine echte ASF-Beispieldatei fehlen, dokumentiere den offenen Punkt und implementiere bis dahin die unabhängig testbaren Module vollständig.

Verwende Platzhalter niemals als scheinbar funktionsfähige Produktivlösung.

Ergänze am Ende einen klaren Implementierungsstatus mit den Kategorien:

- Vollständig implementiert und getestet.
- Implementiert, Allplan-Integrationstest ausstehend.
- Weitere Daten oder Entscheidungen erforderlich.
- Noch nicht umgesetzt.

## 22. Gewünschtes Endergebnis

Ich möchte kein theoretisches Konzept, sondern ein benutzbares, professionell strukturiertes Allplan-2026-PythonPart.

Das Plugin soll nach erfolgreicher Entwicklung und lokaler Validierung folgenden Arbeitsablauf ermöglichen:

**Decke anklicken → Betoneigenschaften prüfen → Grundbewehrung als Matten oder Rundstahl definieren → ASF-Datei laden → Zusammenfassungsabstand wählen → Optimierungsstrategie auswählen → Vorschau kontrollieren → native Allplan-Bewehrung erzeugen.**

Die Anwendung muss einfach zu bedienen sein, technisch nachvollziehbar arbeiten und darf keine statische oder konstruktive Sicherheit vortäuschen.

Beginne mit der Prüfung des vorhandenen Repositories und der offiziellen Allplan-2026-API. Erstelle anschließend die Projektstruktur und beginne mit der tatsächlichen Implementierung. Arbeite so weit wie technisch möglich, ohne für bereits festgelegte Anforderungen wiederholt nachzufragen.