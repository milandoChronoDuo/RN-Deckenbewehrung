"""Conservative rectangular merge candidates with bounded extent and added area."""
from dataclasses import dataclass
from shapely.geometry import box
from .model import CHANNELS, Channel, number, ValidationError
from .base import credited_area


@dataclass(frozen=True)
class Region:
    channel: Channel
    polygon: object
    required: float
    sources: tuple[str, ...]

    def __post_init__(self):
        number(self.required, "Zulagebedarf", strict=True)
        if not self.sources or self.polygon.is_empty or not self.polygon.is_valid or self.polygon.area <= 0:
            raise ValidationError("Ungültiger Zulagebereich")


def deficits(cells, bases):
    return [Region(ch, c.polygon, need, (c.id,)) for c in cells for ch in CHANNELS
            if (need := max(0, c.required[ch]-credited_area(c.polygon, ch, bases))) > 1e-9]


def merge_regions(regions, domain, distance_m=2, max_span_m=12, max_added_fraction=0.35):
    for value, name in ((distance_m, "Abstand"), (max_span_m, "Maximale Ausdehnung"), (max_added_fraction, "Zusatzflächenanteil")):
        number(value, name)
    work = sorted(regions, key=lambda r: (r.channel.face.value, r.channel.direction.value, r.sources))
    while True:
        candidates = []
        for i, a in enumerate(work):
            for j in range(i+1, len(work)):
                b = work[j]
                if a.channel != b.channel or a.polygon.distance(b.polygon) > distance_m*1000:
                    continue
                union = a.polygon.union(b.polygon)
                rect = box(*union.bounds)
                x0,y0,x1,y1 = rect.bounds
                if max(x1-x0, y1-y0) > max_span_m*1000 or not domain.covers(rect):
                    continue
                if rect.area > union.area*(1+max_added_fraction)+1e-6:
                    continue
                # Do not produce overlaps with a third region.
                if any(k not in (i,j) and r.channel == a.channel and rect.intersection(r.polygon).area > 1e-6 for k,r in enumerate(work)):
                    continue
                added_steel_proxy = rect.area*max(a.required,b.required) - a.polygon.area*a.required - b.polygon.area*b.required
                candidates.append((added_steel_proxy,i,j,rect))
        if not candidates:
            return work
        _,i,j,rect = min(candidates, key=lambda c:c[:3])
        a,b = work[i],work[j]
        merged = Region(a.channel,rect,max(a.required,b.required),tuple(sorted(a.sources+b.sources)))
        work = [r for k,r in enumerate(work) if k not in (i,j)] + [merged]
