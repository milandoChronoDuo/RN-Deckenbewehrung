from pathlib import Path
import pytest
from shapely.geometry import box,Polygon
from shapely.ops import unary_union
from rn_deckenbewehrung.asf import read_allplot
from rn_deckenbewehrung.alignment import Alignment,ResultMapping,asf_cells,contour_domain,check_alignment
from rn_deckenbewehrung.geometry import Slab
from rn_deckenbewehrung.model import *
from rn_deckenbewehrung.planning import plan_base_bars,tile_rectangular_mesh
from rn_deckenbewehrung.solid import slab_snapshot
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'tests/fixtures/synthetic-allplot.asf'


def test_asf_structural_reader():
    m=read_allplot(FIX)
    assert len(m.nodes)==4 and len(m.results)==1
    assert m.results[1]==tuple(range(1,16))
    assert m.materials[1][0]=='C_25/30'


@pytest.mark.parametrize('old,new',[
    ('5.0 Nemetschek ALLPLOT','6.0 Nemetschek ALLPLOT'),
    ('GP KNOT 4','GP KNOT 400'),('1 1 2 3 4 1 1','1 1 2 3 99 1 1'),
    ('2 4 0 0','1 4 0 0'),('QM1 0 0','QM1 1 0'),
    ('10 11 12 13 14 15','10 11 12 13 14 nan'),
    ('QM1 0 0 1','QM1 0 0 2'),('QR3 1','QR3 1 1'),
])
def test_asf_rejects_bad_data(tmp_path,old,new):
    p=tmp_path/'bad.asf';p.write_text(FIX.read_text().replace(old,new))
    with pytest.raises(ValidationError):read_allplot(p)


def test_encoding_and_triangle(tmp_path):
    p=tmp_path/'test.asf';p.write_bytes(FIX.read_text().replace('SYNTHETIC TEST MODEL - NO PROJECT DATA','Überlagerung').replace('1 1 2 3 4 1 1','1 1 2 3 0 1 1').encode('cp1252'))
    m=read_allplot(p);assert m.title=='Überlagerung' and m.elements[1][3]==0


def test_explicit_mapping_and_alignment():
    m=read_allplot(FIX);s=Slab('S',box(0,0,4000,3000),500,200)
    transform=Alignment(1000,0,0,0,True)
    # Arbitrary SYNTHETIC contract, not a claimed FRILO column definition.
    mapping=ResultMapping((0,1,2,3),1,m.qr3[0],'SYNTHETIC TEST ONLY',0)
    cs=asf_cells(m,s,transform,mapping)
    assert cs[0].required[CHANNELS[2]]==3
    assert cs[0].polygon.area==12000000
    with pytest.raises(ValidationError): asf_cells(m,s,Alignment(1000,0,0,0),mapping)
    with pytest.raises(ValidationError): asf_cells(m,s,Alignment(1,0,0,0,True),mapping)
    with pytest.raises(ValidationError): asf_cells(m,s,Alignment(1000,0,100,0,True),mapping)
    with pytest.raises(ValidationError): asf_cells(m,s,transform,ResultMapping((0,1,2,3),1,m.qr3[0],'TEST',90))


def test_contours_order_and_holes():
    t=Alignment(1,0,0,0,True)
    outer=[(0,0,0),(10,0,0),(10,10,0),(0,10,0)]
    hole=[(2,2,0),(3,2,0),(3,3,0),(2,3,0)]
    p=contour_domain([hole,outer],t)
    assert len(p.interiors)==1 and p.area==99
    with pytest.raises(ValidationError):contour_domain([outer,outer],t)


def test_base_plan_height_positions_and_hole():
    s=Slab('S',Polygon([(0,0),(4000,0),(4000,3000),(0,3000)], [[(1500,1000),(2500,1000),(2500,2000),(1500,2000)]]),1000,200)
    layer=BarLayer(Channel(Face.BOTTOM,Direction.X),2,BarSpec(10,150))
    bars=plan_base_bars(s,[layer],30,30,30,first_position=10)
    assert bars and all(b.start[2]==1035 for b in bars)
    assert min(b.position for b in bars)==10
    assert len(set(b.position for b in bars))<len(bars)
    with pytest.raises(ValidationError):plan_base_bars(s,[layer],30,30,30,max_length=500)


def test_mesh_tiles_cover_and_overlap():
    domain=box(100,200,10100,7200)
    sheets=tile_rectangular_mesh(domain,6000,2300,400,300)
    assert unary_union([s.footprint for s in sheets]).equals(domain)
    assert all(s.footprint.bounds[2]-s.footprint.bounds[0]<=6000 for s in sheets)
    a,b=[s for s in sheets if s.index_y==0][:2]
    assert a.footprint.intersection(b.footprint).bounds[2]-a.footprint.intersection(b.footprint).bounds[0]==400
    with pytest.raises(ValidationError):tile_rectangular_mesh(domain.difference(box(1000,1000,2000,2000)),6000,2300,400,300)
    with pytest.raises(ValidationError):tile_rectangular_mesh(domain,6000,2300,6000,300)


def cube():
    v=[(x,y,z) for z in (1000,1200) for x,y in ((0,0),(4000,0),(4000,3000),(0,3000))]
    rings=[(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    f=[list(zip(r,r[1:]+r[:1])) for r in rings]
    return v,f


def test_solid_world_height_and_rings():
    v,f=cube();s=slab_snapshot(v,f)
    assert s.bottom_z==1000 and s.thickness==200 and len(s.contours)==1


@pytest.mark.parametrize('change',['slope','open','taper'])
def test_solid_rejects_unsupported(change):
    v,f=cube()
    if change=='slope': v[4]=(0,0,1250)
    if change=='open':f.pop()
    if change=='taper':v[4]=(50,0,1200)
    with pytest.raises(ValidationError):slab_snapshot(v,f)


def test_bundled_runtime_matches_source():
    for name in ('__init__.py','model.py','asf.py','solid.py'):
        assert (ROOT/'src/rn_deckenbewehrung'/name).read_bytes()==(ROOT/'allplan/PythonPartsScripts/rn_deckenbewehrung'/name).read_bytes()


def test_solid_through_opening():
    outer=[(0,0),(4000,0),(4000,3000),(0,3000)]
    inner=[(1000,1000),(2000,1000),(2000,2000),(1000,2000)]
    v=[(x,y,z) for z in (1000,1200) for x,y in outer+inner]
    def edges(r):return list(zip(r,r[1:]+r[:1]))
    f=[edges([0,1,2,3])+edges([4,5,6,7]),edges([8,9,10,11])+edges([12,13,14,15])]
    for ring in ([0,1,2,3],[4,5,6,7]):
        for a,b in edges(ring):f.append(edges([a,b,b+8,a+8]))
    s=slab_snapshot(v,f)
    assert len(s.contours)==2


def test_mapping_is_not_optional():
    with pytest.raises(ValidationError):ResultMapping((0,0,1,2),1,(0,)*12,'test',0)
    with pytest.raises(ValidationError):ResultMapping((0,1,2,3),1,(0,)*12,'',0)


def test_native_snapshot_uses_global_coordinates(monkeypatch):
    import sys,types,importlib.util
    v,f=cube()
    class Edge:
        def __init__(self,p):self.p=p
        def GetStartIndex(self):return self.p[0]
        def GetEndIndex(self):return self.p[1]
    class Face:
        def __init__(self,e):self.e=e
        def GetEdges(self):return self.e
    class Poly:
        def GetVerticesCount(self):return len(v)
        def GetVertex(self,i):return 0,types.SimpleNamespace(X=v[i][0],Y=v[i][1],Z=v[i][2])
        def GetVertices(self):raise AssertionError('Local coordinates must not be used')
        def GetFacesCount(self):return len(f)
        def GetFace(self,i):return Face(f[i])
        def GetEdge(self,e):return 0,Edge(e)
    monkeypatch.setitem(sys.modules,'NemAll_Python_Geometry',types.SimpleNamespace(Polyhedron3D=Poly,eGeometryErrorCode=types.SimpleNamespace(eOK=0)))
    spec=importlib.util.spec_from_file_location('test_slab_adapter',ROOT/'allplan/PythonPartsScripts/RN/SlabGeometry.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    adapter=types.SimpleNamespace(GetModelGeometry=lambda:Poly())
    assert module.extract_slab(adapter).bottom_z==1000
