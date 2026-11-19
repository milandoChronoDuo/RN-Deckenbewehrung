"""Explicit coordinate transform and full contour comparison, never auto-fit."""
from dataclasses import dataclass
from math import cos, sin, radians
from shapely.geometry import Polygon
from .model import ValidationError, number, CHANNELS
from .fem import Cell


@dataclass(frozen=True)
class Alignment:
    scale_to_mm: float
    rotation_deg: float
    dx_mm: float
    dy_mm: float
    confirmed: bool = False

    def __post_init__(self):
        number(self.scale_to_mm,'Längenmaßstab',strict=True)
        for x in (self.rotation_deg,self.dx_mm,self.dy_mm): number(x,'Transformation',minimum=-1e12)

    def xy(self,point):
        x,y=point[:2]; a=radians(self.rotation_deg); k=self.scale_to_mm
        return (k*(cos(a)*x-sin(a)*y)+self.dx_mm,k*(sin(a)*x+cos(a)*y)+self.dy_mm)


def contour_domain(contours, transform):
    """Nesting parity, without relying on ring order or orientation."""
    rings=[Polygon([transform.xy(p) for p in ring]) for ring in contours]
    if not rings or any(not p.is_valid or p.is_empty or p.area<=0 for p in rings):
        raise ValidationError('Ungültige ASF-Konturen')
    for i,p in enumerate(rings):
        for q in rings[i+1:]:
            if p.boundary.intersects(q.boundary): raise ValidationError('Konturen kreuzen oder berühren sich')
    domain=Polygon()
    for p in rings: domain=domain.symmetric_difference(p)
    if domain.geom_type!='Polygon' or not domain.is_valid:
        raise ValidationError('Mehrere getrennte Decken/verschachtelte Inseln noch nicht unterstützt')
    return domain


def check_alignment(model,slab,transform,tolerance_mm=1):
    number(tolerance_mm,'Konturtoleranz',strict=True)
    if not transform.confirmed: raise ValidationError('Koordinatenabgleich ausdrücklich bestätigen')
    z=[p[2] for p in model.nodes.values()]+[p[2] for ring in model.contours for p in ring]
    if (max(z)-min(z))*transform.scale_to_mm>tolerance_mm:
        raise ValidationError('ASF-Netz ist nicht horizontal')
    domain=contour_domain(model.contours,transform)
    if len(domain.interiors)!=len(slab.footprint.interiors):
        raise ValidationError('Anzahl der Öffnungen stimmt nicht überein')
    # Symmetric containment and boundary distance, including openings.
    if (domain.boundary.hausdorff_distance(slab.footprint.boundary)>tolerance_mm
        or not domain.buffer(tolerance_mm).covers(slab.footprint)
        or not slab.footprint.buffer(tolerance_mm).covers(domain)):
        raise ValidationError('ASF-Kontur passt nicht zur Decke: Maßstab, Versatz, Rotation und Öffnungen prüfen')
    return domain


@dataclass(frozen=True)
class ResultMapping:
    """Externally verified import contract; no built-in QM1 mapping inferred.

    columns: zero-based indices in the 15 numeric values AFTER QM1 flags/id,
    ordered as CHANNELS. A verified QR3 tuple is bound exactly to this profile.
    """
    columns: tuple[int,int,int,int]
    area_factor_to_cm2_m: float
    qr3: tuple
    evidence: str
    axes_rotation_deg: float

    def __post_init__(self):
        if len(self.columns)!=4 or len(set(self.columns))!=4 or any(type(i)!=int or not 0<=i<15 for i in self.columns):
            raise ValidationError('Vier eindeutige QM1-Spaltenindizes 0..14 erforderlich')
        number(self.area_factor_to_cm2_m,'As-Einheitenfaktor',strict=True)
        number(self.axes_rotation_deg,'Ergebnisachsen',minimum=-1e12)
        if not self.evidence.strip() or len(self.qr3)!=12: raise ValidationError('Verifizierter QR3-Bezug und Quellenbeleg erforderlich')


def asf_cells(model,slab,transform,mapping):
    from shapely import STRtree
    check_alignment(model,slab,transform)
    if len(model.qr3)!=1 or tuple(model.qr3[0])!=tuple(mapping.qr3):
        raise ValidationError('QR3-Konfiguration weicht vom geprüften Importprofil ab')
    angle=(transform.rotation_deg+mapping.axes_rotation_deg)%180
    if min(angle,180-angle)>1e-8:
        raise ValidationError('Ergebnisrichtungen stimmen nicht mit global X/Y überein; keine skalare As-Rotation')
    cells=[]
    for ident,element in model.elements.items():
        points=[transform.xy(model.nodes[n]) for n in element[:4] if n!=0]
        # Triangle exports may repeat one node. Remove only consecutive duplicates.
        polygon=Polygon(points)
        if not polygon.is_valid or polygon.is_empty or polygon.area<=0:
            raise ValidationError(f'Element {ident}: ungültige Flächengeometrie')
        if not slab.footprint.covers(polygon):
            raise ValidationError(f'Element {ident}: außerhalb der Decke/innerhalb Öffnung; kein stilles Abschneiden')
        required={ch:number(model.results[ident][col]*mapping.area_factor_to_cm2_m,'As') for ch,col in zip(CHANNELS,mapping.columns)}
        cells.append(Cell(str(ident),polygon,required))
    tree=STRtree([c.polygon for c in cells])
    for i,c in enumerate(cells):
        for j in tree.query(c.polygon,predicate='intersects'):
            if j>i and c.polygon.intersection(cells[j].polygon).area>1e-6:
                raise ValidationError('Überlappende FEM-Flächenelemente')
    return cells
