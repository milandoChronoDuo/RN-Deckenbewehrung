from pathlib import Path
from dataclasses import replace
import json
import pytest
from shapely.geometry import box,Polygon
from shapely.ops import unary_union
from rn_deckenbewehrung.model import *
from rn_deckenbewehrung.geometry import Slab
from rn_deckenbewehrung.fem import Cell
from rn_deckenbewehrung.assessment import rectangular_regions,assess,validate_cells
from rn_deckenbewehrung.anchorage import ReviewedLengths
from rn_deckenbewehrung.asf import read_allplot
from rn_deckenbewehrung.alignment import Alignment,ResultMapping
from rn_deckenbewehrung.import_quality import import_cells
from rn_deckenbewehrung.review_report import report
from rn_deckenbewehrung.review_cli import run_project
ROOT=Path(__file__).resolve().parents[1]
CH=CHANNELS[0]
def cell(id,p,v=3):return Cell(id,p,{ch:v if ch==CH else 0 for ch in CHANNELS})
def slab(p=None):return Slab('S',box(0,0,4000,4000) if p is None else p,0,250)


def test_triangles_become_conservative_rectangles():
    cs=[cell('a',Polygon([(0,0),(4000,0),(4000,4000)]),1.1),cell('b',Polygon([(0,0),(4000,4000),(0,4000)]),8.1)]
    rs,issues,missing=rectangular_regions(cs,slab(),grid_mm=500,max_span_mm=2000)
    assert not issues and missing.is_empty
    assert unary_union([r.polygon for r in rs]).equals(slab().footprint)
    for c in cs:
        for r in rs:
            if r.polygon.intersection(c.polygon).area>1e-6:assert r.required>=c.required[CH]
    assert all(max(r.polygon.bounds[2]-r.polygon.bounds[0],r.polygon.bounds[3]-r.polygon.bounds[1])<=2000 for r in rs)


def test_every_positive_need_is_region_or_issue_near_hole():
    s=slab(box(0,0,4000,4000).difference(box(1250,1250,1750,1750)))
    rs,issues,missing=rectangular_regions([cell('a',s.footprint)],s)
    assert any(i.code=='boundary_region' for i in issues)
    covered=unary_union([r.polygon for r in rs]+[i.geometry for i in issues])
    assert covered.equals(s.footprint)
    assert all(s.footprint.covers(r.polygon) for r in rs)


def test_missing_is_unknown_even_with_zero_need():
    rs,issues,missing=rectangular_regions([cell('a',box(0,0,1000,1000),0)],slab())
    assert not rs and missing.area==15000000
    assert issues[0].code=='missing_results'


def test_peak_is_not_averaged_and_channels_do_not_mix():
    c1=cell('a',box(0,0,100,4000),10);c2=cell('b',box(100,0,4000,4000),1)
    c2.required[CHANNELS[3]]=7
    rs,_,_=rectangular_regions([c1,c2],slab())
    assert all(r.required>=10 for r in rs if r.channel==CH and r.polygon.intersection(c1.polygon).area>0)
    assert any(r.channel==CHANNELS[3] and r.required==7 for r in rs)


def test_partial_optimization_reports_all_failures():
    cs=[cell('edge',box(0,0,500,500)),cell('inside',box(1500,1500,2500,2500))]
    a=assess(cs,slab(),[BarSpec(10,150)],{10:ReviewedLengths(300,500,'TEST','TEST','fixture')})
    assert a.proposals and any(i.code=='placement_failed' for i in a.issues)
    assert a.status=='Prüfung erforderlich'
    assert report(a,source_label='TEST')['production_ready'] is False


@pytest.mark.parametrize('change',['missing_channel','nan','duplicate','overlap'])
def test_invalid_results_rejected(change):
    a=cell('a',box(0,0,2000,2000));cs=[a]
    if change=='missing_channel':a.required.pop(CHANNELS[1])
    if change=='nan':a.required[CH]=float('nan')
    if change=='duplicate':cs.append(a)
    if change=='overlap':cs.append(cell('b',box(1000,1000,3000,3000)))
    with pytest.raises(ValidationError):rectangular_regions(cs,slab())


def test_grid_resource_limit():
    with pytest.raises(ValidationError):rectangular_regions([cell('a',slab().footprint)],slab(),grid_mm=1,max_tiles=100)


def test_audited_rounding_correction_and_strict_default():
    m=read_allplot(ROOT/'tests/fixtures/synthetic-allplot.asf')
    m.nodes[2]=(4.0000001,0,0);m.nodes[3]=(4.0000001,3,0)
    s=slab(box(0,0,4000,3000));t=Alignment(1000,0,0,0,True)
    mapping=ResultMapping((0,1,2,3),1,m.qr3[0],'SYNTHETIC',0)
    with pytest.raises(ValidationError):import_cells(m,s,t,mapping)
    out=import_cells(m,s,t,mapping,boundary_tolerance_mm=.001,max_removed_area_mm2=.31)
    assert len(out.corrections)==1
    assert out.corrections[0].removed_area_mm2==pytest.approx(.3,abs=1e-6)
    assert out.cells[0].polygon.equals(s.footprint)
    with pytest.raises(ValidationError):import_cells(m,s,t,mapping,boundary_tolerance_mm=.001,max_removed_area_mm2=.1)


def test_example_cli_contract():
    r=run_project(ROOT/'examples/review-project.json')
    assert r['schema']=='RN-REVIEW-1' and r['production_ready'] is False
    assert r['proposals'] and r['missing_results_mm2']>0


def test_asf_cli_requires_digest_bound_mapping(tmp_path):
    p=json.loads((ROOT/'examples/review-project.json').read_text())
    p['fem']={'type':'allplot5','path':str(ROOT/'tests/fixtures/synthetic-allplot.asf'),'mapping_reviewed':True,'verified_sha256':'wrong'}
    config=tmp_path/'project.json';config.write_text(json.dumps(p))
    with pytest.raises(ValidationError,match='SHA256'):run_project(config)


def test_deterministic_regions_on_reordered_input():
    cs=[cell('a',box(0,0,2000,4000),3),cell('b',box(2000,0,4000,4000),3)]
    a=rectangular_regions(cs,slab())[0];b=rectangular_regions(cs[::-1],slab())[0]
    assert [(r.polygon.wkt,r.required,r.sources) for r in a]==[(r.polygon.wkt,r.required,r.sources) for r in b]


def test_positive_tiny_need_is_not_dropped():
    rs,_,_=rectangular_regions([cell('a',slab().footprint,1e-12)],slab())
    assert rs and all(r.required==.5 for r in rs)


def test_base_credit_and_disabled_channel():
    from rn_deckenbewehrung.base import EffectiveBase
    cs=[cell('a',slab().footprint,3)]
    rs,_,_=rectangular_regions(cs,slab(),[EffectiveBase(CH,slab().footprint,4,'TEST')])
    assert not rs


def test_large_mesh_regions():
    cs=[cell(str(i*90+j),box(i*50,j*50,(i+1)*50,(j+1)*50),3) for i in range(90) for j in range(90)]
    s=slab(box(0,0,4500,4500));rs,issues,missing=rectangular_regions(cs,s,grid_mm=500,max_span_mm=6000)
    assert len(rs)==1 and len(rs[0].sources)==8100 and not issues
