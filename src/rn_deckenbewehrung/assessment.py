"""Conservative FEM-to-region assessment, including unresolved geometry.

Grid maxima never average away local peaks. Missing FEM areas and clipped
boundary tiles remain explicit issues rather than becoming zero demand.
"""
from dataclasses import dataclass
from math import ceil
from shapely import STRtree
from shapely.geometry import box, Polygon
from shapely.ops import unary_union
from .model import CHANNELS, ValidationError, number
from .regions import Region
from .base import credited_area
from .optimizer import optimize, Strategy


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    geometry: object
    channel: object = None
    sources: tuple = ()


@dataclass
class Assessment:
    regions: list
    proposals: list
    issues: list
    missing: object

    @property
    def status(self):
        return 'Prüfung erforderlich' if self.issues else 'Rechenvorschlag – keine Ausführungsfreigabe'


def validate_cells(cells,slab):
    if not cells: raise ValidationError('Keine FEM-Ergebnisse')
    if len({c.id for c in cells})!=len(cells): raise ValidationError('Doppelte FEM-Zell-ID')
    for c in cells:
        p=c.polygon
        if not isinstance(p,Polygon) or p.is_empty or not p.is_valid or p.has_z or p.area<=0:
            raise ValidationError(f'Zelle {c.id}: ungültige Geometrie')
        if not slab.footprint.covers(p): raise ValidationError(f'Zelle {c.id}: außerhalb der Decke')
        if set(c.required)!=set(CHANNELS): raise ValidationError(f'Zelle {c.id}: vier Ergebniskanäle erforderlich')
        for v in c.required.values(): number(v,'As erforderlich')
    tree=STRtree([c.polygon for c in cells])
    for i,c in enumerate(cells):
        for j in tree.query(c.polygon,predicate='intersects'):
            if j>i and c.polygon.intersection(cells[j].polygon).area>1e-6:
                raise ValidationError('Überlappende FEM-Zellen')
    return tree


def rectangular_regions(cells,slab,bases=(),*,grid_mm=500,area_step=0.5,max_span_mm=6000,max_tiles=100000):
    """Return rectangles, issues, missing geometry in deterministic order.

    Every positive deficit is either covered by a rectangle at >= its value
    or represented by a boundary issue. Quantization rounds ONLY upward.
    Coalescing equal-valued row runs and vertical runs is bounded in both axes.
    """
    for v,n in ((grid_mm,'Raster'),(area_step,'As-Stufe'),(max_span_mm,'Maximale Ausdehnung')):number(v,n,strict=True)
    if type(max_tiles)!=int or max_tiles<1:raise ValidationError('Positive Rastergrenze erforderlich')
    if grid_mm>max_span_mm:raise ValidationError('Raster größer als maximale Ausdehnung')
    tree=validate_cells(cells,slab)
    missing=slab.footprint.difference(unary_union([c.polygon for c in cells]))
    issues=[]
    if not missing.is_empty and missing.area>1e-6:
        issues.append(Issue('missing_results','FEM-Ergebnisse fehlen; Bedarf unbekannt.',missing))
    needs=[{ch:max(0,c.required[ch]-credited_area(c.polygon,ch,bases)) for ch in CHANNELS} for c in cells]
    x0,y0,x1,y1=slab.footprint.bounds
    nx,ny=ceil((x1-x0)/grid_mm),ceil((y1-y0)/grid_mm)
    if nx*ny>max_tiles:raise ValidationError('Raster zu fein; maximale Zellenzahl überschritten')
    # Dict per channel: (column,row) -> (conservative demand, source IDs).
    tiles={ch:{} for ch in CHANNELS}
    for iy in range(ny):
        for ix in range(nx):
            tile=box(x0+ix*grid_mm,y0+iy*grid_mm,min(x1,x0+(ix+1)*grid_mm),min(y1,y0+(iy+1)*grid_mm))
            part=tile.intersection(slab.footprint)
            if part.area<=1e-6:continue
            hits=[int(i) for i in tree.query(part,predicate='intersects') if part.intersection(cells[i].polygon).area>1e-6]
            for ch in CHANNELS:
                active=[i for i in hits if needs[i][ch]>0]
                if not active:continue
                need=max(needs[i][ch] for i in active)
                # Do not subtract an epsilon: tiny positive demands still round up.
                quantized=max(need,ceil(need/area_step)*area_step)
                sources=tuple(sorted(cells[i].id for i in active))
                if not slab.footprint.covers(tile):
                    issues.append(Issue('boundary_region','Rand-/Öffnungsbereich benötigt gesonderte Verlegeplanung.',part,ch,sources))
                else:tiles[ch][ix,iy]=(quantized,sources)
    rectangles=[]
    limit=max(1,int(max_span_mm//grid_mm))
    for ch,values in tiles.items():
        remaining=set(values)
        while remaining:
            ix,iy=min(remaining,key=lambda p:(p[1],p[0]));need=values[ix,iy][0]
            width=1
            while width<limit and (ix+width,iy) in remaining and values[ix+width,iy][0]==need:width+=1
            height=1
            while height<limit and all((xx,iy+height) in remaining and values[xx,iy+height][0]==need for xx in range(ix,ix+width)):height+=1
            keys={(xx,yy) for xx in range(ix,ix+width) for yy in range(iy,iy+height)}
            sources=tuple(sorted({s for k in keys for s in values[k][1]}))
            remaining.difference_update(keys)
            rectangles.append(Region(ch,box(x0+ix*grid_mm,y0+iy*grid_mm,min(x1,x0+(ix+width)*grid_mm),min(y1,y0+(iy+height)*grid_mm)),need,sources))
    return rectangles,issues,missing


def assess(cells,slab,specs,lengths_by_diameter,*,bases=(),cover=30,strategy=Strategy.BALANCED,
           grid_mm=500,area_step=.5,max_span_mm=6000):
    if not isinstance(strategy,Strategy):raise ValidationError('Unbekannte Optimierungsstrategie')
    number(cover,'Seitliche Betondeckung')
    regions,issues,missing=rectangular_regions(cells,slab,bases,grid_mm=grid_mm,area_step=area_step,max_span_mm=max_span_mm)
    proposals=[]
    # Keep successful candidates for review, but report every failed region.
    # Pass shared used types through optimizer for consistent strategy scoring.
    used=set()
    for region in sorted(regions,key=lambda r:(-r.required,r.channel.face.value,r.channel.direction.value,r.sources)):
        try:
            result=optimize([region],specs,slab,cover,lengths_by_diameter,strategy,used_specs=used)
            proposals.extend(result);used.add(result[0].spec)
        except ValidationError as exc:
            issues.append(Issue('placement_failed',str(exc),region.polygon,region.channel,region.sources))
    return Assessment(regions,proposals,issues,missing)
