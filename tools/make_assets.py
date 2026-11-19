"""Author reproducible technical vector assets, not Allplan-ready bitmap icons."""
from pathlib import Path
from html import escape
root=Path(__file__).resolve().parents[1]/'docs/assets'
root.mkdir(exist_ok=True)
icons={
 'decke':('Decke auswählen','M4 8H28V25H4Z M17 13L22 24L24 20L29 18Z'),
 'matten':('Mattenbewehrung','M5 5V27 M12 5V27 M20 5V27 M27 5V27 M5 5H27 M5 12H27 M5 20H27 M5 27H27'),
 'rundstahl':('Rundstahl','M4 8H28 M4 16H28 M4 24H28'),
 'oben':('Obere Lage','M4 6H28V26H4Z M7 10H25'),
 'unten':('Untere Lage','M4 6H28V26H4Z M7 22H25'),
 'import':('ASF-Import','M6 3H21L27 9V29H6Z M21 3V9H27 M10 17H23 M18 12L23 17L18 22'),
 'grundbewehrung':('Grundbewehrung','M4 5H28V27H4Z M7 10H25 M7 16H25 M7 22H25'),
 'zulage':('Zulagebewehrung','M4 5H28V27H4Z M10 12H22 M10 16H22 M10 20H22'),
 'zusammenfassen':('Bereiche zusammenfassen','M3 8H11V24H3Z M21 8H29V24H21Z M11 16H21 M14 12L11 16L14 20 M18 12L21 16L18 20'),
 'stahlmenge':('Stahlmenge optimieren','M4 25H28 M8 25V16H13V25 M19 25V9H24V25 M7 5L12 10L17 5'),
 'verlegen':('Verlegeaufwand optimieren','M5 7H27 M5 16H27 M5 25H27 M9 4V28'),
 'verankerung':('Verankerung','M4 23H22V9H27 M4 6H20 M4 3V9 M20 3V9'),
 'aussparung':('Aussparung','M3 3H29V29H3Z M12 11H20V21H12Z M6 7H26 M6 16H10 M22 16H26 M6 25H26'),
 'vorschau':('Vorschau','M2 16Q16 0 30 16Q16 32 2 16Z M12 12H20V20H12Z'),
 'erzeugen':('Bewehrung erzeugen','M4 5H28V27H4Z M8 16L14 22L25 10'),
 'hinweis':('Prüfhinweis','M16 3L30 28H2Z M16 11V19 M16 23V25')}
for name,(label,path) in icons.items():
    (root/f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" role="img"><title>{escape(label)}</title><path d="{path}" fill="none" stroke="#172d3d" stroke-width="2" stroke-linejoin="round"/></svg>')

def diagram(name,title,body):
    (root/f'hilfe-{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" role="img"><title>{title}</title><rect width="800" height="360" fill="white"/><g font-family="sans-serif" font-size="20" fill="#172d3d"><text x="24" y="34">{title}</text>{body}<text x="24" y="340" font-size="15">Schema · keine Bemessungswerte · nicht maßstäblich</text></g></svg>')
diagram('lagen','Reihenfolge der Rundstahllagen', '<rect x="45" y="70" width="380" height="230" fill="#f2f4f5" stroke="#172d3d"/><path d="M65 100H405 M65 130H405" stroke="#a14215" stroke-width="8"/><path d="M65 240H405 M65 270H405" stroke="#12628a" stroke-width="8"/><text x="450" y="108">Oben 1 · oberste Lage</text><text x="450" y="138">Oben 2 · darunter</text><text x="450" y="248">Unten 2 · darüber</text><text x="450" y="278">Unten 1 · unterste Lage</text>')
diagram('matten','Mattenübergreifung längs und quer','<rect x="55" y="75" width="330" height="150" fill="#12628a" fill-opacity=".2" stroke="#12628a"/><rect x="310" y="75" width="330" height="150" fill="#12628a" fill-opacity=".2" stroke="#12628a"/><rect x="55" y="175" width="330" height="120" fill="#a14215" fill-opacity=".2" stroke="#a14215"/><text x="410" y="270">Quer: Überdeckung in Y</text><text x="300" y="60">Längs: Überdeckung in X</text>')
diagram('bereiche','Zusammenfassung ist eine geprüfte Option','<rect x="60" y="90" width="200" height="160" fill="none" stroke="#12628a" stroke-width="3"/><rect x="400" y="90" width="200" height="160" fill="none" stroke="#12628a" stroke-width="3"/><path d="M260 170H400 M260 160V180 M400 160V180" stroke="#172d3d" stroke-width="2"/><text x="285" y="150">Abstand</text><rect x="50" y="80" width="560" height="180" fill="none" stroke="#a14215" stroke-dasharray="8 8"/><text x="60" y="300">Zusatzstahl, Öffnungen und Gesamtausdehnung prüfen.</text>')
diagram('anker','Verankerung über den Bedarfsbereich hinaus','<rect x="240" y="90" width="300" height="160" fill="#12628a" fill-opacity=".15"/><path d="M80 170H710" stroke="#a14215" stroke-width="7"/><path d="M80 210H240 M540 210H710" stroke="#172d3d" stroke-width="2"/><text x="90" y="240">Verankerung</text><text x="550" y="240">Verankerung</text><text x="270" y="120">Bedarfsbereich</text><text x="80" y="290">Beide Enden müssen innerhalb der zulässigen Geometrie liegen.</text>')
diagram('oeffnung','Stäbe an Öffnungen unterbrechen','<rect x="50" y="65" width="670" height="220" fill="#f2f4f5" stroke="#172d3d"/><rect x="310" y="120" width="140" height="110" fill="white" stroke="#172d3d"/><path d="M70 95H700 M70 150H280 M480 150H700 M70 200H280 M480 200H700 M70 260H700" stroke="#12628a" stroke-width="5"/><text x="65" y="315">Randabstand und Verankerung prüfen; Randbewehrung separat planen.</text>')
diagram('bedarf','Bedarf und vorgesehener Querschnitt','<path d="M70 70V280H730" fill="none" stroke="#172d3d" stroke-width="2"/><path d="M110 280V190H210V280 M300 280V110H400V280 M490 280V160H590V280" fill="#12628a"/><path d="M90 170H230 M280 90H420 M470 140H610" stroke="#a14215" stroke-width="6"/><text x="80" y="60">As [cm²/m]</text><text x="80" y="310">Blau: FEM-Bedarf · Braun: vorgesehenes As (nur schematisch)</text>')
