"""Validate a horizontal prismatic solid snapshot using only stdlib.

Vertices are world coordinates in mm. Faces contain edge endpoint indices,
which avoids assumptions about Allplan face-loop orientation/ordering.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from .model import ValidationError, number


@dataclass(frozen=True)
class SlabSnapshot:
    bottom_z: float
    thickness: float
    contours: tuple


def _boundary(vertices,faces,level,tolerance):
    counts=Counter()
    for face in faces:
        if all(abs(vertices[n][2]-level)<=tolerance for edge in face for n in edge):
            counts.update(tuple(sorted(e)) for e in face)
    if not counts or any(v>2 for v in counts.values()): raise ValidationError('Ungültige horizontale Flächentopologie')
    edges={e for e,count in counts.items() if count==1}
    neighbors=defaultdict(set)
    for a,b in edges: neighbors[a].add(b);neighbors[b].add(a)
    if any(len(ns)!=2 for ns in neighbors.values()): raise ValidationError('Offene/verzweigte Deckenkontur')
    rings=[]
    while edges:
        a,b=min(edges); start=a; ring=[a]
        while True:
            edges.remove(tuple(sorted((a,b))));ring.append(b)
            if b==start: break
            nexts=[n for n in neighbors[b] if tuple(sorted((b,n))) in edges]
            if len(nexts)!=1: raise ValidationError('Kontur nicht geschlossen')
            a,b=b,nexts[0]
        rings.append(tuple(vertices[n][:2] for n in ring))
    return tuple(rings)


def slab_snapshot(vertices,faces,tolerance=0.01):
    number(tolerance,'Geometrietoleranz',strict=True)
    if len(vertices)<6 or not faces: raise ValidationError('Kein geschlossener Deckenkörper')
    for p in vertices:
        if len(p)!=3: raise ValidationError('3D-Punkt erforderlich')
        for v in p:number(v,'Koordinate',minimum=-1e12)
    for f in faces:
        if len(f)<3 or any(len(e)!=2 or any(type(n)!=int or n<0 or n>=len(vertices) for n in e) for e in f):
            raise ValidationError('Ungültige Flächenkante')
    incidence=Counter(tuple(sorted(e)) for f in faces for e in f)
    if any(n!=2 for n in incidence.values()): raise ValidationError('Körper ist nicht geschlossen')
    lo=min(p[2] for p in vertices); hi=max(p[2] for p in vertices)
    if hi-lo<=2*tolerance or any(min(abs(p[2]-lo),abs(p[2]-hi))>tolerance for p in vertices):
        raise ValidationError('Nur horizontale Decken konstanter Dicke ohne Vertiefungen unterstützt')
    bottom=_boundary(vertices,faces,lo,tolerance);top=_boundary(vertices,faces,hi,tolerance)
    def edges_xy(rings):
        return sorted(tuple(sorted((a,b))) for ring in rings for a,b in zip(ring,ring[1:]))
    # Exact XY parity avoids accepting a tapered solid within a loose tolerance.
    if edges_xy(bottom)!=edges_xy(top): raise ValidationError('Ober-/Unterkontur unterscheiden sich; keine prismatische Decke')
    for f in faces:
        indices=set(n for e in f for n in e)
        pts=[vertices[n] for n in indices]
        if all(abs(p[2]-pts[0][2])<=tolerance for p in pts): continue
        # All projected side-face points must lie on one straight line.
        xy=list(set(p[:2] for p in pts))
        if len(xy)>2:
            a,b=xy[:2]; dx=b[0]-a[0];dy=b[1]-a[1]
            if any(abs(dx*(p[1]-a[1])-dy*(p[0]-a[0]))>tolerance*(dx*dx+dy*dy)**.5 for p in xy[2:]):
                raise ValidationError('Nicht vertikale Seitenfläche')
    return SlabSnapshot(lo,hi-lo,bottom)
