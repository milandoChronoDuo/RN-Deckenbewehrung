import json
from math import pi
from pathlib import Path
import pytest
from shapely.geometry import Polygon, box, LineString
from rn_deckenbewehrung.model import *
from rn_deckenbewehrung.geometry import Slab, bar_segments, extended_segment
from rn_deckenbewehrung.base import EffectiveBase, MeshRecord, select_mesh, credited_area
from rn_deckenbewehrung.fem import read_test_data, read_asf
from rn_deckenbewehrung.regions import Region, deficits, merge_regions
from rn_deckenbewehrung.optimizer import optimize, Strategy
from rn_deckenbewehrung.anchorage import ReviewedLengths, automatic_lengths
from rn_deckenbewehrung.workflow import PreviewGate, delete_owned_elements
from rn_deckenbewehrung.demo import run

CH=Channel(Face.BOTTOM,Direction.X)
ROOT=Path(__file__).resolve().parents[1]


def slab(holes=()):
    return Slab('demo',Polygon([(0,0),(8000,0),(8000,6000),(0,6000)],holes),100,250)


def lengths():
    return {d:ReviewedLengths(300,500,'TEST','TEST','Test fixture only') for d in (8,10,12,14,16)}


def test_area_units():
    assert BarSpec(10,150).area == pytest.approx(pi*100/4*10/150)


@pytest.mark.parametrize('value',[0,-1,float('nan'),float('inf'),True])
def test_bad_specs(value):
    with pytest.raises(ValidationError): BarSpec(value,150)


@pytest.mark.parametrize('holes', [[],[[(2500,2000),(3500,2000),(3500,3000),(2500,3000)]],
    [[(2500,2000),(3500,2000),(3500,3000),(2500,3000)],[(4500,2000),(5500,2000),(5500,4000),(4500,4000)]]])
@pytest.mark.parametrize('direction',list(Direction))
def test_all_bars_respect_cover_and_openings(holes,direction):
    s=slab(holes)
    bars=list(bar_segments(s,BarSpec(12,200),direction,30))
    assert bars
    for b in bars:
        assert s.footprint.covers(b)
        assert b.distance(s.footprint.boundary) >= 36-1e-6  # conservative compensation for GEOS arc approximation
    if holes:
        assert len(bars)>25


def test_concave_slab():
    s=Slab('L',Polygon([(0,0),(6000,0),(6000,2000),(2000,2000),(2000,6000),(0,6000)]),0,200)
    assert all(s.footprint.covers(b) for b in bar_segments(s,BarSpec(10,150),Direction.X,30))


def test_invalid_slab():
    with pytest.raises(ValidationError):
        Slab('bad',Polygon([(0,0),(1,1),(0,1),(1,0)]),0,200)


def layers(enabled=(True,True,True,True)):
    return [BarLayer(ch,1 if ch.direction==Direction.X else 2,BarSpec(10,150),enabled[i]) for i,ch in enumerate(CHANNELS)]


def test_four_layer_axes():
    axes=layer_axes(layers(),100,250,30,40)
    assert [z for _,z in axes] == [135,145,305,295]


def test_disabled_first_recompacts_without_direction_change():
    axes=layer_axes(layers((False,True,False,True)),0,250,30,30)
    assert [(l.channel.direction,z) for l,z in axes] == [(Direction.Y,35),(Direction.Y,215)]


def test_no_base_layers():
    assert layer_axes(layers((False,)*4),0,250,30,30)==[]


def test_collision():
    with pytest.raises(ValidationError): layer_axes(layers(),0,50,30,30)


@pytest.mark.parametrize('bottom,top',[(True,True),(True,False),(False,True),(False,False)])
def test_mesh_selection_independent(bottom,top):
    m=MeshRecord('TEST',3,5,'Synthetic catalog')
    catalog={'TEST':m}
    assert select_mesh('TEST' if bottom else None,catalog)==(m if bottom else None)
    assert select_mesh('TEST' if top else None,catalog)==(m if top else None)
    assert m.area_x != m.area_y


def test_missing_mesh():
    with pytest.raises(ValidationError): select_mesh('unknown',{})


def cells(): return read_test_data(ROOT/'examples/fem-test.json',slab(),alignment_confirmed=True)


def test_deficit_and_partial_credit():
    cs=cells()
    b=EffectiveBase(CH,cs[0].polygon,6,'TEST')
    assert not any(r.sources==('A',) and r.channel==CH for r in deficits(cs,[b]))
    b=EffectiveBase(CH,cs[0].polygon,2,'TEST')
    assert next(r for r in deficits(cs,[b]) if r.sources==('A',) and r.channel==CH).required==3
    assert credited_area(cs[0].polygon,CH,[EffectiveBase(CH,box(1000,1000,1500,2500),9,'TEST')])==0


def test_overlapping_base_is_not_counted_twice():
    b=EffectiveBase(CH,box(0,0,4000,4000),3,'TEST')
    with pytest.raises(ValidationError): credited_area(box(1000,1000,2000,2000),CH,[b,b])


def region(x=1000,ch=CH): return Region(ch,box(x,1000,x+1000,2000),5,(str(x),))


def test_near_regions_merge():
    rs=merge_regions([region(),region(2200)],slab().footprint)
    assert len(rs)==1 and rs[0].required==5


def test_far_regions_do_not_merge():
    assert len(merge_regions([region(),region(4500)],slab().footprint))==2


def test_merge_respects_channel_hole_and_chain_limit():
    assert len(merge_regions([region(),region(2200,Channel(Face.TOP,Direction.X))],slab().footprint))==2
    domain=slab().footprint.difference(box(2050,1200,2150,1800))
    assert len(merge_regions([region(),region(2200)],domain))==2
    rs=merge_regions([region(500+i*1100) for i in range(6)],slab().footprint,max_span_m=2.5)
    assert len(rs)>=3


def test_optimizer_coverage_and_mass():
    result=optimize([region()],[BarSpec(12,150),BarSpec(10,100)],slab(),30,lengths())
    p=result[0]
    assert p.spec.area>=5
    assert p.mass_kg==pytest.approx(sum(b.length for b in p.bars)*pi*p.spec.diameter**2/4*7.85e-6)
    assert all(slab().axis_domain(30,p.spec.diameter).covers(b) for b in p.bars)


def test_strategies_have_different_decisions():
    r=Region(CH,box(1000,1000,2000,4000),5,('R',))
    specs=[BarSpec(8,100),BarSpec(12,200)]
    steel=optimize([r],specs,slab(),30,lengths(),Strategy.STEEL)[0]
    labour=optimize([r],specs,slab(),30,lengths(),Strategy.LABOUR)[0]
    assert steel.spec!=labour.spec
    assert steel.mass_kg < labour.mass_kg
    assert len(labour.bars)<len(steel.bars)


def test_insufficient_diameter():
    with pytest.raises(ValidationError): optimize([region()],[BarSpec(8,200)],slab(),30,lengths())


def test_missing_anchorage():
    with pytest.raises(ValidationError): optimize([region()],[BarSpec(12,150)],slab(),30,{})
    with pytest.raises(NotImplementedError): automatic_lengths()
    with pytest.raises(ValidationError): ReviewedLengths(400,600,'','','')


def test_anchor_and_stock_failure():
    with pytest.raises(ValidationError): extended_segment(LineString([(100,100),(7000,100)]),300,slab().footprint)
    with pytest.raises(ValidationError): optimize([region()],[BarSpec(12,150)],slab(),30,lengths(),max_length=1000)


def test_asf_is_not_silently_json():
    with pytest.raises(NotImplementedError,match='FRILO'): read_asf('real.asf')


def test_fem_alignment_required():
    with pytest.raises(ValidationError): read_test_data(ROOT/'examples/fem-test.json',slab())
    moved=Slab('demo',box(50000,0,58000,6000),0,250)
    with pytest.raises(ValidationError): read_test_data(ROOT/'examples/fem-test.json',moved,alignment_confirmed=True)


@pytest.mark.parametrize('mutation',['missing','nan','units','duplicate','hole','axes'])
def test_fem_bad_data(tmp_path,mutation):
    data=json.loads((ROOT/'examples/fem-test.json').read_text())
    s=slab()
    if mutation=='missing': del data['cells'][0]['required']['oben_X']
    if mutation=='nan': data['cells'][0]['required']['oben_X']=float('nan')
    if mutation=='units': data['units']['length']='m'
    if mutation=='duplicate': data['cells'].append(data['cells'][0])
    if mutation=='hole': s=slab([[(1200,1200),(1400,1200),(1400,1400),(1200,1400)]])
    if mutation=='axes': data['axes']='local'
    path=tmp_path/'bad.json'; path.write_text(json.dumps(data))
    with pytest.raises(ValidationError): read_test_data(path,s,alignment_confirmed=True)


def test_preview_gate_and_duplicates():
    g=PreviewGate(); token=g.preview({'d':10})
    with pytest.raises(ValidationError): g.require_ready(token,[])
    g.confirm(token); g.require_ready(token,[])
    with pytest.raises(ValidationError): g.require_ready(token,['run-1'])
    g.preview({'d':12})
    with pytest.raises(ValidationError): g.confirm(token)
    with pytest.raises(NotImplementedError): delete_owned_elements()


def test_demo():
    result=run(ROOT/'examples/fem-test.json')
    assert result['proposals'] and result['uncovered_area_mm2']>0
    assert all(p['provided_cm2_m']>=p['required_cm2_m'] for p in result['proposals'])


def test_svg_preview():
    from rn_deckenbewehrung.preview import render_svg
    from xml.etree.ElementTree import fromstring
    plans=optimize([region()],[BarSpec(12,150)],slab(),30,lengths())
    svg=render_svg(slab(),cells(),plans,CH)
    assert fromstring(svg).tag.endswith('svg')
    assert 'TESTDATEN' in svg and 'As erforderlich' in svg


def test_generated_palette_and_assets_parse():
    from xml.etree.ElementTree import parse
    palette=parse(ROOT/'allplan/Library/RN/Deckenbewehrung.pyp')
    names=[n.text for n in palette.findall('.//Parameter/Name')]
    assert len(names)==len(set(names))
    for svg in (ROOT/'docs/assets').glob('*.svg'):
        assert parse(svg).getroot().tag.endswith('svg')
