"""Native Allplan factories, not connected to production writing yet.

All coordinates mm. Caller supplies checked geometry, catalog grades, existing
position numbers and selected layer properties. Allplan integration test pending.
No CreateElements/ModifyElements/DeleteElements calls here.
"""
from math import atan2, degrees, hypot, isfinite
import NemAll_Python_Geometry as Geo
import NemAll_Python_Reinforcement as Reinf
import StdReinfShapeBuilder.GeneralReinfShapeBuilder as Shapes
from StdReinfShapeBuilder.ConcreteCoverProperties import ConcreteCoverProperties
from StdReinfShapeBuilder.ReinforcementShapeProperties import ReinforcementShapeProperties
from StdReinfShapeBuilder.RotationAngles import RotationAngles


def straight_bar(start, end, diameter, position, steel_grade, concrete_grade, bending_roller):
    if position < 1 or diameter <= 0 or bending_roller <= 0:
        raise ValueError('Position, Durchmesser und Biegerolle prüfen')
    if not all(isfinite(v) for v in (*start, *end, diameter, bending_roller)):
        raise ValueError('Nicht endliche Stabkoordinaten')
    if start[2] != end[2]:
        raise ValueError('Nur horizontale Stäbe unterstützt')
    length = hypot(end[0]-start[0], end[1]-start[1])
    if length <= 0:
        raise ValueError('Stablänge muss positiv sein')
    props = ReinforcementShapeProperties.rebar(
        diameter, bending_roller, steel_grade, concrete_grade,
        Reinf.BendingShapeType.LongitudinalBar)
    shape = Shapes.create_longitudinal_shape_with_hooks(
        length, RotationAngles(0, 0, degrees(atan2(end[1]-start[1], end[0]-start[0]))),
        props, ConcreteCoverProperties.all(0), start_hook=-1, end_hook=-1)
    shape.Move(Geo.Vector3D(*start))
    return Reinf.BarPlacement(position, 1, Geo.Vector3D(), Geo.Point3D(), Geo.Point3D(), shape)


def rectangular_mesh(mesh_name, length, width, origin, position, common_properties):
    """One unrotated catalog sheet; no implicit tiling, splicing or hole cutting."""
    if not mesh_name or position < 1 or not all(isfinite(v) for v in (length,width,*origin)) or min(length,width) <= 0:
        raise ValueError('Mattenparameter ungültig')
    data = Reinf.ReinforcementShapeBuilder.GetMeshData(mesh_name)
    if data.Length <= 0 or data.Width <= 0 or length > data.Length or width > data.Width:
        raise ValueError('Matte fehlt im Katalog oder Zuschnitt überschreitet Katalogabmessungen')
    x,y,z = origin
    polygon = Geo.Polygon3D()
    for px,py in ((x,y),(x+length,y),(x+length,y+width),(x,y+width),(x,y)):
        polygon += Geo.Point3D(px,py,z)
    placement = Reinf.PlaneMeshPlacement(position,data,length,width,polygon)
    placement.CommonProperties = common_properties
    return placement


def bars_from_plan(bars, common_properties_by_face, steel_grade, concrete_grade, bending_roller,
                   occupied_positions=()):
    """Prepare all native elements in memory; does not write to the document.

    Caller must obtain actual selected CommonProperties from Allplan and a fresh
    occupied-position inventory. No default/fabricated layer IDs are supplied.
    """
    bars=tuple(bars)
    if any(b.position in occupied_positions for b in bars):
        raise ValueError('Positionsnummer bereits im Modell belegt')
    for face in {b.channel.face for b in bars}:
        if face not in common_properties_by_face:
            raise ValueError(f'Allplan-Layer/Format für {face.value} fehlt')
    shapes={}
    for b in bars:
        key=(b.diameter,hypot(b.end[0]-b.start[0],b.end[1]-b.start[1]))
        if b.position in shapes and shapes[b.position]!=key:
            raise ValueError('Unterschiedliche Formen mit gleicher Positionsnummer')
        shapes[b.position]=key
    result=[]
    for b in bars:
        placement=straight_bar(b.start,b.end,b.diameter,b.position,steel_grade,concrete_grade,bending_roller)
        placement.CommonProperties=common_properties_by_face[b.channel.face]
        result.append(placement)
    return result
