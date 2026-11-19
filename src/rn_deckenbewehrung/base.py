"""Spatially explicit credit; callers must supply verified effective footprints."""
from dataclasses import dataclass
from shapely.geometry import Polygon
from .model import Channel, ValidationError, number


@dataclass(frozen=True)
class EffectiveBase:
    channel: Channel
    footprint: Polygon
    area: float
    evidence: str

    def __post_init__(self):
        number(self.area, "Wirksames As")
        if not self.evidence.strip() or self.footprint.is_empty or not self.footprint.is_valid:
            raise ValidationError("Wirksamer Grundbewehrungsbereich benötigt gültige Geometrie und Nachweis")


def credited_area(cell, channel, bases):
    """Conservative cell credit: only fully covered cells, never partial averages.

    Duplicate overlapping footprints of the same channel are rejected to prevent
    crediting mesh overlaps twice. Separate layers use separate channels.
    """
    matching = [b for b in bases if b.channel == channel]
    for i, base in enumerate(matching):
        for other in matching[i+1:]:
            if base.footprint.intersection(other.footprint).area > 1e-6:
                raise ValidationError("Überlappende Grundbewehrungsnachweise: doppelte Anrechnung möglich")
    return max((b.area for b in matching if b.footprint.covers(cell)), default=0)


@dataclass(frozen=True)
class MeshRecord:
    name: str
    area_x: float
    area_y: float
    catalog_reference: str

    def __post_init__(self):
        number(self.area_x, "Matte As X", strict=True)
        number(self.area_y, "Matte As Y", strict=True)
        if not self.name or not self.catalog_reference:
            raise ValidationError("Geprüfter Mattenkatalogeintrag erforderlich")


def select_mesh(name, catalog):
    if name is None:
        return None
    if name not in catalog:
        raise ValidationError(f"Matte {name} fehlt im bereitgestellten Katalog")
    return catalog[name]
