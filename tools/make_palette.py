"""Generate the diagnostic Allplan palette; production options are disabled."""
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, indent, ElementTree
ROOT = Path(__file__).resolve().parents[1]
e = Element('Element', {'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance', 'xsi:noNamespaceSchemaLocation':'https://pythonparts.allplan.com/2026/schemas/PythonPart.xsd'})
s = SubElement(e,'Script')
for k,v in {'Name':r'RN\Deckenbewehrung.py','Title':'RN Deckenbewehrung · Entwicklungsstand','Version':'0.2','ReadLastInput':'False'}.items():
    SubElement(s,k).text=v
page=SubElement(e,'Page')
SubElement(page,'Name').text='Main'
SubElement(page,'Text').text='Deckenbewehrung'
p=SubElement(page,'Parameters')
def param(parent,name,label,value,kind='String',**extra):
    n=SubElement(parent,'Parameter')
    for k,v in dict(Name=name,Text=label,Value=value,ValueType=kind,**extra).items():
        SubElement(n,k).text=str(v)
    return n
param(p,'Status','Status','Decke im Modell auswählen.',Enable='False')
param(p,'Thickness','Erkannte Deckenstärke','Noch nicht ermittelt','String',Enable='False')
param(p,'BottomZ','Unterkante [Weltkoordinaten]','Noch nicht ermittelt',Enable='False')
param(p,'TopZ','Oberkante [Weltkoordinaten]','Noch nicht ermittelt',Enable='False')
param(p,'Scope','Funktionsumfang','Geometrie- und ASF-Prüfung; keine Erzeugung.',Enable='False')
param(p,'Mode','Grundbewehrung','Rundstahl','StringComboBox',ValueList='Rundstahl|Matten')
for face,label in [('Bottom','Unten'),('Top','Oben')]:
    group=param(p,face+'Mesh',label+' · Matten','','Expander',Visible="Mode == 'Matten'")
    gp=SubElement(group,'Parameters')
    param(gp,face+'MeshEnabled','Matte verwenden','False','CheckBox',Enable='False')
    param(gp,face+'MeshType','Mattentyp aus Allplan-Katalog','','ReinfMeshType',Enable='False')
    group=param(p,face+'Bars',label+' · Rundstahl','','Expander',Visible="Mode == 'Rundstahl'")
    gp=SubElement(group,'Parameters')
    for i in (1,2):
        param(gp,face+str(i)+'Enabled',f'{i}. Lage aktiv','False','CheckBox',Enable='False')
        param(gp,face+str(i)+'Diameter',f'{i}. Lage · Durchmesser [mm]',10,'Double',Enable='False')
        param(gp,face+str(i)+'Spacing',f'{i}. Lage · Abstand [mm]',150,'Length',Enable='False')
param(p,'AsfPath','FRILO-ASF-Datei','','String',ValueDialog='OpenFileDialog',FileFilter='ASF-Dateien (*.asf)|*.asf|',FileExtension='asf')
param(p,'ImportStatus','ASF-Prüfung','Keine Datei gewählt.',Enable='False')
indent(e)
ElementTree(e).write(ROOT/'allplan/Library/RN/Deckenbewehrung.pyp',encoding='utf-8',xml_declaration=True)
