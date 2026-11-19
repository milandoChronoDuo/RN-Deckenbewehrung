"""Structural reader for the observed ALLPLOT 5.0 FRILO export dialect.

No automatic QM1 column semantics, norm-ID translation or unit inference.
Unknown extension records are counted, not interpreted as reinforcement.
Only standard library imports so inspection can also run inside Allplan.
"""
from dataclasses import dataclass, field
from collections import Counter
from pathlib import Path
from hashlib import sha256
from math import isfinite
from .model import ValidationError


@dataclass
class AsfModel:
    title: str
    digest: str
    contours: list = field(default_factory=list)
    nodes: dict = field(default_factory=dict)
    elements: dict = field(default_factory=dict)
    results: dict = field(default_factory=dict)
    qr3: list = field(default_factory=list)
    materials: dict = field(default_factory=dict)
    properties: dict = field(default_factory=dict)
    norm_id: tuple = ()
    other_records: Counter = field(default_factory=Counter)

    def summary(self):
        points = list(self.nodes.values())
        return {'format':'ALLPLOT 5.0', 'title':self.title, 'sha256':self.digest,
                'contours':len(self.contours),'nodes':len(self.nodes),'elements':len(self.elements),
                'qm1_records':len(self.results),'qm1_values_per_record':sorted({len(r) for r in self.results.values()}),
                'coordinate_bounds_raw':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],
                'norm_id_raw':self.norm_id,'qr3_raw':self.qr3,
                'materials_raw':self.materials,'element_properties_raw':self.properties,
                'other_record_counts':dict(self.other_records),
                'status':'Struktur gelesen; Einheiten, QR3- und QM1-Bedeutung noch explizit zu verifizieren.'}


def _floats(tokens, line):
    try:
        values=tuple(float(t) for t in tokens)
    except ValueError as exc:
        raise ValidationError(f'ASF Zeile {line}: Zahl erwartet') from exc
    if not all(isfinite(v) for v in values):
        raise ValidationError(f'ASF Zeile {line}: nicht endlicher Wert')
    return values


def _ints(tokens,line):
    try:
        return tuple(int(t) for t in tokens)
    except ValueError as exc:
        raise ValidationError(f'ASF Zeile {line}: Ganzzahl erwartet') from exc


def read_allplot(path):
    """Read counted geometry tables and observed QM1 records without guessing.

    Limits protect the interactive host from accidental huge input. Column
    layout is strict for the supported tables; other record types stay opaque.
    """
    path=Path(path)
    if path.stat().st_size > 64*1024*1024:
        raise ValidationError('ASF-Datei größer als 64 MiB')
    raw=path.read_bytes()
    try: text=raw.decode('utf-8-sig')
    except UnicodeDecodeError: text=raw.decode('cp1252')
    lines=text.splitlines()
    if len(lines)<2 or lines[0].strip()!='5.0 Nemetschek ALLPLOT':
        raise ValidationError('Unterstützt wird derzeit ALLPLOT 5.0')
    model=AsfModel(lines[1].strip(),sha256(raw).hexdigest())
    i=2; seen=set()
    while i<len(lines):
        t=lines[i].split(); line=i+1; i+=1
        if not t: continue
        key=' '.join(t[:2]) if t[0] in ('GL','GP','GF') else t[0]
        if key in ('GL POLY','GP KNOT','GF ELEM','MATERIAL','ELEMENT_PROPERTIES'):
            prefix=2 if t[0] in ('GL','GP','GF') else 1
            if len(t)!=prefix+1: raise ValidationError(f'ASF Zeile {line}: ungültiger Tabellenkopf')
            count,=_ints(t[prefix:],line)
            if count<1 or count>1000000 or i+count>len(lines):
                raise ValidationError(f'ASF Zeile {line}: ungültige/abgeschnittene Tabelle')
            if key!='GL POLY':
                if key in seen: raise ValidationError(f'Doppelte ASF-Tabelle: {key}')
                seen.add(key)
            rows=[]
            for offset in range(count):
                values=lines[i+offset].split(); n=i+offset+1
                expected={'GL POLY':3,'GP KNOT':4,'GF ELEM':7,'MATERIAL':12,'ELEMENT_PROPERTIES':4}[key]
                if len(values)!=expected: raise ValidationError(f'ASF Zeile {n}: {key} erwartet {expected} Felder')
                if key=='GL POLY': rows.append(_floats(values,n)); continue
                ident,=_ints(values[:1],n)
                target={'GP KNOT':model.nodes,'GF ELEM':model.elements,'MATERIAL':model.materials,'ELEMENT_PROPERTIES':model.properties}[key]
                if ident<=0 or ident in target: raise ValidationError(f'ASF Zeile {n}: ungültige/doppelte ID')
                if key=='GP KNOT': target[ident]=_floats(values[1:],n)
                elif key=='GF ELEM': target[ident]=_ints(values[1:],n)
                elif key=='MATERIAL':
                    _floats(values[2:6]+values[7:],n)
                    target[ident]=tuple(values[1:])
                else:
                    _floats(values[1:3],n); _ints(values[3:],n)
                    target[ident]=tuple(values[1:])
            if key=='GL POLY': model.contours.append(tuple(rows))
            i+=count
        elif key=='NORM_ID':
            if model.norm_id: raise ValidationError('Doppelte NORM_ID')
            model.norm_id=_ints(t[1:],line)
        elif key=='QR3':
            if len(t)!=13: raise ValidationError(f'ASF Zeile {line}: unbekannte QR3-Variante')
            model.qr3.append(_floats(t[1:],line))
        elif key=='QM1':
            if len(t)!=19: raise ValidationError(f'ASF Zeile {line}: unbekannte QM1-Variante')
            a,b,ident=_ints(t[1:4],line)
            if (a,b)!=(0,0): raise ValidationError('QM1-Flags werden noch nicht unterstützt')
            if ident in model.results: raise ValidationError('Doppelte QM1-Element-ID')
            model.results[ident]=_floats(t[4:],line)
        else:
            if t[0][0].isalpha(): model.other_records[key]+=1
    if not model.nodes or not model.elements or not model.contours or not model.qr3:
        raise ValidationError('ASF: erforderliche Geometrie-/QR3-Tabelle fehlt')
    if set(model.results)!=set(model.elements):
        raise ValidationError('QM1-Ergebnisse fehlen oder verweisen auf unbekannte Elemente')
    for ident,element in model.elements.items():
        if any(n not in model.nodes for n in element[:3]) or (element[3]!=0 and element[3] not in model.nodes):
            raise ValidationError(f'Element {ident}: unbekannter Knoten')
    return model
