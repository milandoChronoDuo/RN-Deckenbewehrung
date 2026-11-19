"""Planar slab geometry. Shapely/GEOS is isolated from the Allplan adapter."""
from dataclasses import dataclass
from math import ceil, cos, pi
from shapely.geometry import Polygon, LineString
from .model import ValidationError, Direction, number


@dataclass(frozen=True)
class Slab:
    id: str
    footprint: Polygon
    bottom_z: float
    thickness: float

    def __post_init__(self):
        p = self.footprint
        if not self.id or not isinstance(p, Polygon) or p.is_empty or not p.is_valid or p.has_z or p.area <= 0:
            raise ValidationError("Ungültige ebene Deckenkontur oder Öffnungen")
        number(self.bottom_z, "Unterkante", minimum=-1e12)
        number(self.thickness, "Dicke", strict=True)
        for x, y in p.exterior.coords:
            number(x, "X", minimum=-1e12)
            number(y, "Y", minimum=-1e12)

    def axis_domain(self, cover, diameter):
        number(cover, "Seitliche Betondeckung")
        number(diameter, "Durchmesser", strict=True)
        # Round erosion: conservative clearance from concave corners and holes.
        radius = (cover + diameter / 2) / cos(pi / 128)
        domain = self.footprint.buffer(-radius, quad_segs=32)
        if domain.is_empty:
            raise ValidationError("Kein Platz für Stabachsen bei dieser Betondeckung")
        return domain


def line_parts(geometry):
    if geometry.geom_type == "LineString":
        if geometry.length > 1e-6:
            yield geometry
    elif hasattr(geometry, "geoms"):
        for part in geometry.geoms:
            yield from line_parts(part)


def bar_segments(slab, spec, direction, cover):
    """Clip each row against eroded footprint, splitting rows at all holes.

    Equal spacing <= requested spacing; both boundary rows included.
    No anchorage capacity is implied by the clipped segments.
    """
    if direction not in (Direction.X, Direction.Y):
        raise ValidationError("Unbekannte Stabrichtung")
    domain = slab.axis_domain(cover, spec.diameter)
    x0, y0, x1, y1 = domain.bounds
    lo, hi = (y0, y1) if direction == Direction.X else (x0, x1)
    count = max(1, ceil((hi-lo) / spec.spacing))
    if count > 100000:
        raise ValidationError("Zu viele Stabreihen; Einheiten und Abstand prüfen")
    for index in range(count+1):
        t = lo + (hi-lo) * index/count
        line = LineString([(x0-1, t), (x1+1, t)]) if direction == Direction.X else LineString([(t, y0-1), (t, y1+1)])
        yield from line_parts(domain.intersection(line))


def extended_segment(segment, length, domain):
    """Never silently trim an anchorage at a slab edge or opening."""
    number(length, "Verankerungslänge")
    a, b = segment.coords[0], segment.coords[-1]
    dx, dy = (b[0]-a[0])/segment.length, (b[1]-a[1])/segment.length
    extended = LineString([(a[0]-dx*length, a[1]-dy*length), (b[0]+dx*length, b[1]+dy*length)])
    if not domain.covers(extended):
        raise ValidationError("Erforderliche Verankerung überschreitet Rand oder Öffnung")
    return extended
