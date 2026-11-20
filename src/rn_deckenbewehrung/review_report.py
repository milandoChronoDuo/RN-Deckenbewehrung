"""Serializable review report: partial successes must never mask unresolved demand."""
from dataclasses import asdict
from shapely.geometry import mapping
from .model import CHANNELS


def channel_name(ch):return f'{ch.face.value}_{ch.direction.value}' if ch else None


def report(assessment,*,source_label,imported=None):
    return {
        'schema':'RN-REVIEW-1','status':assessment.status,'source':source_label,
        'production_ready':False,
        'limitations':['Keine Normfreigabe.','Zulagenhöhen und räumliche Kollisionen noch nicht geprüft.',
                       'Keine produktive Allplan-Modellerzeugung.'],
        'missing_results_mm2':assessment.missing.area,
        'missing_geometry':mapping(assessment.missing),
        'boundary_corrections':[] if imported is None else [asdict(c) for c in imported.corrections],
        'channels':{channel_name(ch):{
            'regions':sum(r.channel==ch for r in assessment.regions),
            'proposals':sum(p.region.channel==ch for p in assessment.proposals),
            'issues':sum(i.channel==ch for i in assessment.issues)} for ch in CHANNELS},
        'issues':[{'code':i.code,'message':i.message,'channel':channel_name(i.channel),'sources':i.sources,'geometry':mapping(i.geometry)} for i in assessment.issues],
        'proposals':[{'channel':channel_name(p.region.channel),'sources':p.region.sources,
                      'region':mapping(p.region.polygon),'required_cm2_m':p.region.required,
                      'provided_cm2_m':p.spec.area,'diameter_mm':p.spec.diameter,
                      'maximum_spacing_mm':p.spec.spacing,'mass_kg':p.mass_kg,
                      'bars':[list(b.coords) for b in p.bars]} for p in assessment.proposals]
    }
