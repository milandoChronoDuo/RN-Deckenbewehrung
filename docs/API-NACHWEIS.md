# Allplan-API-Nachweise

Recherche: 19.11.2026. Offizielles Repository
https://github.com/NemetschekAllplan/PythonPartsExamples, Branch `2026`,
Commit `e816b120038ca121b51d80b78f22da561b5c6fda`.
Die verwendeten Beispielsignaturen wurden vor der Implementierung gelesen.
Es wurden keine Allplan-SDK-Dateien in dieses Repository kopiert.

| Eigene Verwendung | Offizielles Beispiel unter PythonPartsExampleScripts |
|---|---|
| BaseScriptObject, create_script_object, start_input/start_next_input, SingleElementSelectResult, SingleElementSelectInteractor(result, [Slab_TypeUUID], prompt) | ArchitectureExamples/ModifyObjects/ModifySlab.py |
| GetElement(adapter), slab.Properties, TierCount, GetSlabTierProperties(i).Thickness | ArchitectureExamples/ModifyObjects/ModifySlab.py |
| CreateElementResult(elements), OnCancelFunctionResult.CANCEL_INPUT | ArchitectureExamples/ModifyObjects/ModifySlab.py |
| ReinforcementShapeProperties.rebar(diameter, bending_roller, steel_grade, concrete_grade, BendingShapeType.LongitudinalBar) | ReinforcementExamples/BarPlacement/LongitudinalBarPlacement.py |
| create_longitudinal_shape_with_hooks(length, RotationAngles, shape_props, ConcreteCoverProperties.all(0), start_hook=-1, end_hook=-1), shape.Move(Vector3D) | ReinforcementExamples/BarPlacement/LongitudinalBarPlacement.py |
| BarPlacement(position, count, Vector3D, Point3D, Point3D, shape) | ReinforcementExamples/BarPlacement/LongitudinalBarPlacement.py |
| GetMeshData(name), data.Length/Width, PlaneMeshPlacement(position, data, length, width, polygon), CommonProperties | ReinforcementExamples/MeshPlacement/PlaneMeshPlacement.py |

Die API-Referenz zu BarPlacement wurde zusätzlich abgerufen:
https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_Reinforcement/BarPlacement/

Palette: XML-Struktur, Sichtbarkeitsausdrücke und ReinfMeshType aus den
entsprechenden offiziellen Library/Examples/PythonParts-Beispielen.
Die generierte PYP wurde gegen diese offiziellen Schemata validiert:
https://pythonparts.allplan.com/2026/schemas/PythonPart.xsd
https://pythonparts.allplan.com/2026/schemas/PythonPartParameter.xsd

Der Nachweis einer existierenden Signatur ersetzt keinen Laufzeittest.
Insbesondere lokale Formachsen/Rotation, erzeugte Stablängen, Mattenlage,
Versionsargument und Auswahlabbruch müssen lokal geprüft werden.

Nicht verifiziert und deshalb nicht aufgerufen: Extraktion aller Öffnungen
in Weltkoordinaten, atomare Erzeugungs-/Rollback-Semantik, persistente
Elementzuordnung und sichere Löschung, Plugin-Manager-Paketformat sowie
Icon-Einbindung. Allgemeine Dokumentation: https://pythonparts.allplan.com/2026/
