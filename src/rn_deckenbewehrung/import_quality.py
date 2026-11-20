"""Opt-in, measured clipping of coordinate-rounding slivers, never hole filling."""
from dataclasses import dataclass
from shapely.geometry import Polygon
from shapely.ops import unary_union
from .model import ValidationError,number,CHANNELS
from .fem import Cell
from .alignment import check_alignment
from .assessment import validate_cells


@dataclass(frozen=True)
class BoundaryCorrection:
    cell_id: str
    removed_area_mm2: float
    tolerance_mm: float


@dataclass(frozen=True)
class ImportedCells:
    cells: tuple
    corrections: tuple
    missing: object


def import_cells(model,slab,transform,mapping,*,boundary_tolerance_mm=0,max_removed_area_mm2=0):
    """Both bounds must be explicitly supplied to permit rounding correction.

    Output keeps an audit record per corrected cell and explicit uncovered area.
    This does not verify the provenance/meaning of a user-supplied ResultMapping.
    """
    number(boundary_tolerance_mm,'Randtoleranz');number(max_removed_area_mm2,'Maximale Korrekturfläche')
    check_alignment(model,slab,transform)
    if len(model.qr3)!=1 or tuple(model.qr3[0])!=tuple(mapping.qr3):raise ValidationError('QR3 stimmt nicht mit geprüftem Profil überein')
    angle=(transform.rotation_deg+mapping.axes_rotation_deg)%180
    if min(angle,180-angle)>1e-8:raise ValidationError('Ergebnisachsen stimmen nicht mit global X/Y überein')
    cells=[];corrections=[];removed=0
    for ident,e in model.elements.items():
        p=Polygon([transform.xy(model.nodes[n]) for n in e[:4] if n])
        if not p.is_valid or p.is_empty or p.area<=0:raise ValidationError(f'Element {ident}: ungültig')
        if not slab.footprint.covers(p):
            if boundary_tolerance_mm==0 or not slab.footprint.buffer(boundary_tolerance_mm).covers(p):
                raise ValidationError(f'Element {ident}: außerhalb erlaubter Randtoleranz')
            clipped=p.intersection(slab.footprint)
            removed_area=p.difference(slab.footprint).area;removed+=removed_area
            if removed>max_removed_area_mm2 or clipped.geom_type!='Polygon' or clipped.is_empty:
                raise ValidationError('Korrekturfläche überschritten oder Zelle durch Öffnung geteilt')
            corrections.append(BoundaryCorrection(str(ident),removed_area,boundary_tolerance_mm));p=clipped
        required={ch:number(model.results[ident][col]*mapping.area_factor_to_cm2_m,'As erforderlich') for ch,col in zip(CHANNELS,mapping.columns)}
        cells.append(Cell(str(ident),p,required))
    validate_cells(cells,slab)
    return ImportedCells(tuple(cells),tuple(corrections),slab.footprint.difference(unary_union([c.polygon for c in cells])))
