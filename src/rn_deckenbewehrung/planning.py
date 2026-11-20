"""Pure planning of native-adapter input, not a construction approval."""
from dataclasses import dataclass
from math import ceil
from shapely.geometry import box
from .geometry import bar_segments
from .model import layer_axes, ValidationError, number


@dataclass(frozen=True)
class PlannedBar:
    start: tuple
    end: tuple
    diameter: float
    channel: object
    position: int


def plan_base_bars(slab,layers,bottom_cover,top_cover,side_cover,*,first_position=1,max_length=12000,clear_gap=0):
    if type(first_position)!=int or first_position<1: raise ValidationError('Positive Startposition erforderlich')
    number(max_length,'Maximale Stablänge',strict=True)
    bars=[]; marks={}
    for layer,z in layer_axes(layers,slab.bottom_z,slab.thickness,bottom_cover,top_cover,clear_gap):
        for line in bar_segments(slab,layer.spec,layer.channel.direction,side_cover):
            if line.length>max_length: raise ValidationError('Grundstab überschreitet Lieferlänge; Stoßplanung erforderlich')
            # Exact lengths only; avoid grouping different shapes by rounding.
            key=(layer.channel,layer.spec.diameter,line.length)
            if key not in marks: marks[key]=first_position+len(marks)
            a,b=line.coords[0],line.coords[-1]
            bars.append(PlannedBar((*a,z),(*b,z),layer.spec.diameter,layer.channel,marks[key]))
    return bars


@dataclass(frozen=True)
class MeshSheet:
    footprint: object
    index_x: int
    index_y: int


def tile_rectangular_mesh(domain,sheet_length,sheet_width,lap_x,lap_y):
    """Rectangular slab, unrotated stock sheets, explicit reviewed overlaps.

    Nonrectangular footprints/holes are rejected, never covered by a bbox.
    Cutting native meshes around holes needs a separate verified adapter.
    """
    for n,v in [('Länge',sheet_length),('Breite',sheet_width),('Stoß X',lap_x),('Stoß Y',lap_y)]: number(v,n,strict=True)
    if lap_x>=sheet_length or lap_y>=sheet_width: raise ValidationError('Übergreifung muss kleiner als Mattenabmessung sein')
    if domain.is_empty or not domain.is_valid or not domain.equals(box(*domain.bounds)):
        raise ValidationError('Mattenaufteilung derzeit nur für Rechteck ohne Öffnungen')
    x0,y0,x1,y1=domain.bounds
    nx=max(1,ceil((x1-x0-sheet_length)/(sheet_length-lap_x))+1)
    ny=max(1,ceil((y1-y0-sheet_width)/(sheet_width-lap_y))+1)
    if nx*ny>100000: raise ValidationError('Zu viele Matten; Einheiten prüfen')
    return [MeshSheet(box(x0+i*(sheet_length-lap_x),y0+j*(sheet_width-lap_y),
                          min(x1,x0+i*(sheet_length-lap_x)+sheet_length),
                          min(y1,y0+j*(sheet_width-lap_y)+sheet_width)),i,j)
            for i in range(nx) for j in range(ny)]
