"""Run synthetic calculation and write reviewable JSON; not a design approval."""
import argparse
import json
from pathlib import Path
from shapely.geometry import box
from .geometry import Slab
from .model import BarSpec
from .fem import read_test_data
from .regions import deficits, merge_regions
from .optimizer import optimize, Strategy
from .anchorage import ReviewedLengths


def run(path, strategy=Strategy.BALANCED):
    slab = Slab('demo',box(0,0,8000,6000),0,250)
    cells = read_test_data(path,slab,alignment_confirmed=True)
    regions = merge_regions(deficits(cells,[]),slab.footprint)
    specs = [BarSpec(d,s) for d in (8,10,12,14,16) for s in (100,150,200)]
    # Deliberately synthetic values, not results of a normative calculation.
    lengths = {d:ReviewedLengths(400,600,'TEST','TEST','Synthetisch; kein Normnachweis') for d in (8,10,12,14,16)}
    plans = optimize(regions,specs,slab,30,lengths,strategy)
    return {'status':'TESTDATEN – keine Ausführungsfreigabe','strategy':strategy.value,
            'uncovered_area_mm2':slab.footprint.area-sum(c.polygon.area for c in cells),
            'notes':['FEM-Daten decken nur Teilbereiche ab.', 'Lagenkollisionen, Normnachweise und Mattenstöße nicht geprüft.'],
            'proposals':[{'face':p.region.channel.face.value,'direction':p.region.channel.direction.value,
                          'sources':p.region.sources,'required_cm2_m':p.region.required,
                          'provided_cm2_m':p.spec.area,'diameter_mm':p.spec.diameter,
                          'spacing_max_mm':p.spec.spacing,'mass_kg':p.mass_kg,'score':p.score,
                          'bars':[list(b.coords) for b in p.bars]} for p in plans]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--strategy',choices=[s.value for s in Strategy],default='ausgewogen')
    args=parser.parse_args()
    args.output.write_text(json.dumps(run(args.input,Strategy(args.strategy)),ensure_ascii=False,indent=2),encoding='utf-8')


if __name__ == '__main__':
    main()
