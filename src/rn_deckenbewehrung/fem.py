"""Explicit synthetic JSON format. This is NOT a FRILO ASF parser."""
import json
from dataclasses import dataclass
from pathlib import Path
from shapely.geometry import Polygon
from .model import CHANNELS, ValidationError, number


@dataclass(frozen=True)
class Cell:
    id: str
    polygon: Polygon
    required: dict


def read_asf(path):
    from .asf import read_allplot
    return read_allplot(path)


def read_test_data(path, slab, *, alignment_confirmed=False):
    if not alignment_confirmed:
        raise ValidationError("Koordinaten, Maßstab und X/Y-Richtungen zuerst bestätigen")
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("format") != "RN-SYNTHETIC-FEM-1" or data.get("units") != {"length": "mm", "area": "cm2/m"}:
        raise ValidationError("Nur gekennzeichnete RN-Testdaten mit eindeutigen Einheiten zulässig")
    if data.get("slab_id") != slab.id or data.get("axes") != "global_X_Y":
        raise ValidationError("Deckenbezug oder Ergebnisrichtungen passen nicht")
    cells, ids = [], set()
    for item in data["cells"]:
        polygon = Polygon(item["polygon"])
        if not polygon.is_valid or polygon.is_empty or polygon.area <= 0 or polygon.has_z or not slab.footprint.covers(polygon):
            raise ValidationError("FEM-Zelle außerhalb der Decke, in Öffnung oder ungültig")
        if item["id"] in ids:
            raise ValidationError("Doppelte FEM-Zell-ID")
        ids.add(item["id"])
        required = {}
        for channel in CHANNELS:
            key = f"{channel.face.value}_{channel.direction.value}"
            if key not in item["required"]:
                raise ValidationError(f"Fehlender FEM-Ergebniswert: {key}")
            required[channel] = number(item["required"][key], key)
        if any(polygon.intersection(c.polygon).area > 1e-6 for c in cells):
            raise ValidationError("Überlappende FEM-Zellen")
        cells.append(Cell(item["id"], polygon, required))
    if not cells:
        raise ValidationError("Keine FEM-Ergebnisse")
    return cells
