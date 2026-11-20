"""Enumerated candidate optimization with transparent units and hard constraints.

Rectangular regions only. End anchorage must fit the eroded domain. No automatic
laps: bars exceeding stock length are rejected. Layer collision must be checked
by the caller before production; this module returns proposals only.
"""
from dataclasses import dataclass
from enum import Enum
from math import ceil, pi
from shapely.geometry import box, LineString
from .model import Direction, ValidationError, number
from .geometry import extended_segment


class Strategy(str, Enum):
    STEEL = "stahl"
    BALANCED = "ausgewogen"
    LABOUR = "verlegeaufwand"


@dataclass(frozen=True)
class Proposal:
    region: object
    spec: object
    bars: tuple
    mass_kg: float
    score: float


def optimize(regions, specs, slab, cover, lengths_by_diameter, strategy=Strategy.BALANCED,
             max_spacing=250, max_length=12000, min_clear=25, used_specs=()):
    if not isinstance(strategy, Strategy):
        raise ValidationError("Unbekannte Optimierungsstrategie")
    for v,n in ((max_spacing,"Maximaler Abstand"),(max_length,"Maximale Länge"),(min_clear,"Lichter Abstand")):
        number(v,n,strict=True)
    # kg-equivalent penalties per placed bar and new diameter/spacing type.
    weights = {Strategy.STEEL:(0,0), Strategy.BALANCED:(0.15,3), Strategy.LABOUR:(2,30)}
    bar_weight, type_weight = weights[strategy]
    selected, used = [], set(used_specs)
    for region in sorted(regions, key=lambda r:(-r.required,r.channel.face.value,r.channel.direction.value,r.sources)):
        if not region.polygon.equals(box(*region.polygon.bounds)):
            raise ValidationError("Optimierung benötigt rechteckige Bereiche; polygonale Bereiche zuerst aufteilen")
        options = []
        x0,y0,x1,y1 = region.polygon.bounds
        for spec in specs:
            if spec.area+1e-9 < region.required or spec.spacing > max_spacing or spec.spacing-spec.diameter < min_clear:
                continue
            lengths = lengths_by_diameter.get(spec.diameter)
            if lengths is None:
                continue
            domain = slab.axis_domain(cover,spec.diameter)
            transverse = y1-y0 if region.channel.direction == Direction.X else x1-x0
            intervals = max(1,ceil(transverse/spec.spacing))
            if intervals > 100000 or transverse/intervals-spec.diameter < min_clear:
                continue
            bars = []
            try:
                for i in range(intervals+1):
                    t = i/intervals
                    line = LineString([(x0,y0+t*(y1-y0)),(x1,y0+t*(y1-y0))]) if region.channel.direction == Direction.X else LineString([(x0+t*(x1-x0),y0),(x0+t*(x1-x0),y1)])
                    bar = extended_segment(line,lengths.anchorage,domain)
                    if bar.length > max_length:
                        raise ValidationError("Stablänge überschritten; Stoßplanung erforderlich")
                    bars.append(bar)
            except ValidationError:
                continue
            mass = sum(b.length for b in bars)*pi*spec.diameter**2/4*7.85e-6
            score = mass + bar_weight*len(bars) + type_weight*(spec not in used)
            options.append(Proposal(region,spec,tuple(bars),mass,score))
        if not options:
            raise ValidationError(f"Keine zulässige Kombination für {region.sources}; As, Verankerung und Einbaubarkeit prüfen")
        best = min(options,key=lambda p:(p.score,p.mass_kg,p.spec.diameter,p.spec.spacing))
        selected.append(best)
        used.add(best.spec)
    return selected
