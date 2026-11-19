<?xml version='1.0' encoding='utf-8'?>
<Element xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://pythonparts.allplan.com/2026/schemas/PythonPart.xsd">
  <Script>
    <Name>RN\Deckenbewehrung.py</Name>
    <Title>RN Deckenbewehrung · Entwicklungsstand</Title>
    <Version>0.1</Version>
    <ReadLastInput>False</ReadLastInput>
  </Script>
  <Page>
    <Name>Main</Name>
    <Text>Deckenbewehrung</Text>
    <Parameters>
      <Parameter>
        <Name>Status</Name>
        <Text>Status</Text>
        <Value>Decke im Modell auswählen.</Value>
        <ValueType>String</ValueType>
        <Enable>False</Enable>
      </Parameter>
      <Parameter>
        <Name>Thickness</Name>
        <Text>Erkannte Deckenstärke</Text>
        <Value>Noch nicht ermittelt</Value>
        <ValueType>String</ValueType>
        <Enable>False</Enable>
      </Parameter>
      <Parameter>
        <Name>Scope</Name>
        <Text>Funktionsumfang</Text>
        <Value>Auswahlprüfung; keine Bewehrungserzeugung.</Value>
        <ValueType>String</ValueType>
        <Enable>False</Enable>
      </Parameter>
      <Parameter>
        <Name>Mode</Name>
        <Text>Grundbewehrung</Text>
        <Value>Rundstahl</Value>
        <ValueType>StringComboBox</ValueType>
        <ValueList>Rundstahl|Matten</ValueList>
      </Parameter>
      <Parameter>
        <Name>BottomMesh</Name>
        <Text>Unten · Matten</Text>
        <Value />
        <ValueType>Expander</ValueType>
        <Visible>Mode == 'Matten'</Visible>
        <Parameters>
          <Parameter>
            <Name>BottomMeshEnabled</Name>
            <Text>Matte verwenden</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>BottomMeshType</Name>
            <Text>Mattentyp aus Allplan-Katalog</Text>
            <Value />
            <ValueType>ReinfMeshType</ValueType>
            <Enable>False</Enable>
          </Parameter>
        </Parameters>
      </Parameter>
      <Parameter>
        <Name>BottomBars</Name>
        <Text>Unten · Rundstahl</Text>
        <Value />
        <ValueType>Expander</ValueType>
        <Visible>Mode == 'Rundstahl'</Visible>
        <Parameters>
          <Parameter>
            <Name>Bottom1Enabled</Name>
            <Text>1. Lage aktiv</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>Bottom1Diameter</Name>
            <Text>1. Lage · Durchmesser [mm]</Text>
            <Value>10</Value>
            <ValueType>Double</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>Bottom1Spacing</Name>
            <Text>1. Lage · Abstand [mm]</Text>
            <Value>150</Value>
            <ValueType>Length</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>Bottom2Enabled</Name>
            <Text>2. Lage aktiv</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>Bottom2Diameter</Name>
            <Text>2. Lage · Durchmesser [mm]</Text>
            <Value>10</Value>
            <ValueType>Double</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>Bottom2Spacing</Name>
            <Text>2. Lage · Abstand [mm]</Text>
            <Value>150</Value>
            <ValueType>Length</ValueType>
            <Enable>False</Enable>
          </Parameter>
        </Parameters>
      </Parameter>
      <Parameter>
        <Name>TopMesh</Name>
        <Text>Oben · Matten</Text>
        <Value />
        <ValueType>Expander</ValueType>
        <Visible>Mode == 'Matten'</Visible>
        <Parameters>
          <Parameter>
            <Name>TopMeshEnabled</Name>
            <Text>Matte verwenden</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>TopMeshType</Name>
            <Text>Mattentyp aus Allplan-Katalog</Text>
            <Value />
            <ValueType>ReinfMeshType</ValueType>
            <Enable>False</Enable>
          </Parameter>
        </Parameters>
      </Parameter>
      <Parameter>
        <Name>TopBars</Name>
        <Text>Oben · Rundstahl</Text>
        <Value />
        <ValueType>Expander</ValueType>
        <Visible>Mode == 'Rundstahl'</Visible>
        <Parameters>
          <Parameter>
            <Name>Top1Enabled</Name>
            <Text>1. Lage aktiv</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>Top1Diameter</Name>
            <Text>1. Lage · Durchmesser [mm]</Text>
            <Value>10</Value>
            <ValueType>Double</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>Top1Spacing</Name>
            <Text>1. Lage · Abstand [mm]</Text>
            <Value>150</Value>
            <ValueType>Length</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>Top2Enabled</Name>
            <Text>2. Lage aktiv</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>Top2Diameter</Name>
            <Text>2. Lage · Durchmesser [mm]</Text>
            <Value>10</Value>
            <ValueType>Double</ValueType>
            <Enable>False</Enable>
          </Parameter>
          <Parameter>
            <Name>Top2Spacing</Name>
            <Text>2. Lage · Abstand [mm]</Text>
            <Value>150</Value>
            <ValueType>Length</ValueType>
            <Enable>False</Enable>
          </Parameter>
        </Parameters>
      </Parameter>
      <Parameter>
        <Name>ImportStatus</Name>
        <Text>FRILO-ASF</Text>
        <Value>Beispieldatei und Formatprüfung fehlen.</Value>
        <ValueType>String</ValueType>
        <Enable>False</Enable>
      </Parameter>
    </Parameters>
  </Page>
</Element>