"""Documented 2026 polyhedron access; global GetVertex, NOT local GetVertices."""
import NemAll_Python_Geometry as Geo
from rn_deckenbewehrung.solid import slab_snapshot
from rn_deckenbewehrung.model import ValidationError


def extract_slab(adapter):
    poly=adapter.GetModelGeometry()
    if not isinstance(poly,Geo.Polyhedron3D):
        raise ValidationError('Deckengeometrie ist kein unterstützter Polyhedron3D')
    vertices=[]
    for i in range(poly.GetVerticesCount()):
        error,p=poly.GetVertex(i)
        if error!=Geo.eGeometryErrorCode.eOK: raise ValidationError('Allplan: Deckeneckpunkt nicht lesbar')
        vertices.append((p.X,p.Y,p.Z))
    faces=[]
    for i in range(poly.GetFacesCount()):
        edges=[]
        for oriented in poly.GetFace(i).GetEdges():
            error,edge=poly.GetEdge(oriented)
            if error!=Geo.eGeometryErrorCode.eOK: raise ValidationError('Allplan: Deckenkante nicht lesbar')
            edges.append((edge.GetStartIndex(),edge.GetEndIndex()))
        faces.append(edges)
    return slab_snapshot(vertices,faces)
