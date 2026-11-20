"""Run a reproducible review from an explicit project input JSON.

Real ASF input requires a file-bound, externally verified mapping. The example
uses labeled synthetic data only. The CLI never writes Allplan model elements.
"""
import argparse,json
from pathlib import Path
from shapely.geometry import shape
from .model import BarSpec,ValidationError
from .geometry import Slab
from .fem import read_test_data
from .asf import read_allplot
from .alignment import Alignment,ResultMapping
from .import_quality import import_cells
from .anchorage import ReviewedLengths
from .assessment import assess
from .optimizer import Strategy
from .review_report import report


def run_project(path):
    path=Path(path);data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('schema')!='RN-PROJECT-1':raise ValidationError('Unbekanntes Projektformat')
    if data.get('units')!='mm_cm2_per_m':raise ValidationError('Projekteinheiten müssen mm und cm²/m sein')
    slab_data=data['slab'];slab=Slab(slab_data['id'],shape(slab_data['footprint']),slab_data['bottom_z_mm'],slab_data['thickness_mm'])
    source=data['fem'];file=path.parent/source['path'];imported=None
    if source['type']=='synthetic':
        cells=read_test_data(file,slab,alignment_confirmed=source.get('alignment_confirmed') is True)
        label='Synthetische Testdaten – keine Bemessungsgrundlage'
    elif source['type']=='allplot5':
        model=read_allplot(file)
        if source.get('verified_sha256')!=model.digest or source.get('mapping_reviewed') is not True:
            raise ValidationError('ASF-Datei und Ergebnisprofil müssen ausdrücklich geprüft und per SHA256 gebunden sein')
        transform=Alignment(**source['alignment'])
        mapping_data=source['mapping'];mapping=ResultMapping(tuple(mapping_data['columns']),mapping_data['area_factor_to_cm2_m'],tuple(mapping_data['qr3']),mapping_data['evidence'],mapping_data['axes_rotation_deg'])
        imported=import_cells(model,slab,transform,mapping,**source.get('boundary_policy',{}));cells=imported.cells
        label=f'ALLPLOT 5.0 · SHA256 {model.digest} · Profilnachweis: {mapping.evidence}'
    else:raise ValidationError('Unbekannter FEM-Quelltyp')
    specs=[BarSpec(*pair) for pair in data['combinations_mm']]
    lengths={float(d):ReviewedLengths(**values) for d,values in data['reviewed_lengths_mm'].items()}
    assessment=assess(cells,slab,specs,lengths,strategy=Strategy(data['strategy']),**data['assessment'])
    return report(assessment,source_label=label,imported=imported)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        result=run_project(args.project)
    except (ValidationError,KeyError,TypeError,ValueError,OSError) as exc:
        parser.exit(2,f'Prüfung abgebrochen: {exc}\n')
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(f"{result['status']}: {len(result['proposals'])} Vorschläge, {len(result['issues'])} offene Prüfpunkte.")


if __name__=='__main__':main()
