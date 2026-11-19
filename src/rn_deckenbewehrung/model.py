"""Immutable domain values; no Allplan imports."""
from dataclasses import dataclass
from enum import Enum
from math import isfinite, pi


class ValidationError(ValueError):
    """Input cannot be used safely."""


def number(value, name, minimum=0, strict=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValidationError(f"{name}: endliche Zahl erforderlich")
    if value < minimum or (strict and value == minimum):
        raise ValidationError(f"{name}: muss {'größer als' if strict else 'mindestens'} {minimum} sein")
    return value


class Face(str, Enum):
    BOTTOM = "unten"
    TOP = "oben"


class Direction(str, Enum):
    X = "X"
    Y = "Y"


@dataclass(frozen=True)
class Channel:
    face: Face
    direction: Direction

    def __post_init__(self):
        if not isinstance(self.face, Face) or not isinstance(self.direction, Direction):
            raise ValidationError("Lage/Richtung ungültig")


CHANNELS = tuple(Channel(f, d) for f in Face for d in Direction)


@dataclass(frozen=True)
class BarSpec:
    diameter: float
    spacing: float

    def __post_init__(self):
        number(self.diameter, "Durchmesser", strict=True)
        number(self.spacing, "Abstand", strict=True)
        if self.spacing <= self.diameter:
            raise ValidationError("Stababstand muss größer als Durchmesser sein")

    @property
    def area(self):
        # mm²/bar × 1000 mm/m ÷ spacing mm ÷ 100 mm²/cm²
        return pi * self.diameter**2 / 4 * 10 / self.spacing


@dataclass(frozen=True)
class BarLayer:
    channel: Channel
    order: int
    spec: BarSpec
    enabled: bool = True

    def __post_init__(self):
        if self.order not in (1, 2):
            raise ValidationError("Lagennummer muss 1 oder 2 sein")


def layer_axes(layers, bottom_z, thickness, bottom_cover, top_cover, clear_gap=0):
    """Recompact active layers; directions stay attached to their input layers."""
    number(bottom_z, "Unterkante", minimum=-1e12)
    number(thickness, "Dicke", strict=True)
    for name, value in (("Deckung unten", bottom_cover), ("Deckung oben", top_cover), ("Lagenabstand", clear_gap)):
        number(value, name)
    result = []
    extents = {}
    for face, cover in ((Face.BOTTOM, bottom_cover), (Face.TOP, top_cover)):
        active = sorted((l for l in layers if l.enabled and l.channel.face == face), key=lambda l: l.order)
        if len({l.order for l in active}) != len(active) or len({l.channel.direction for l in active}) != len(active):
            raise ValidationError("Doppelte oder nicht orthogonale Lagen")
        offset = cover
        for layer in active:
            axis = offset + layer.spec.diameter / 2
            z = bottom_z + (axis if face == Face.BOTTOM else thickness - axis)
            result.append((layer, z))
            offset += layer.spec.diameter + clear_gap
        extents[face] = offset - (clear_gap if active else 0)
    if sum(extents.values()) + clear_gap > thickness:
        raise ValidationError("Bewehrungslagen passen nicht in die Decke")
    return result
