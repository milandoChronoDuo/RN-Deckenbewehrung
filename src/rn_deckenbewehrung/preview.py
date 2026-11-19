"""SVG ground-plan review for synthetic FEM inputs; no replacement reinforcement."""
from html import escape


def polygon_path(polygon):
    rings = [polygon.exterior, *polygon.interiors]
    return ' '.join('M '+' L '.join(f'{x:g},{y:g}' for x,y in ring.coords)+' Z' for ring in rings)


def render_svg(slab, cells, proposals, channel):
    x0,y0,x1,y1=slab.footprint.bounds
    margin=max(x1-x0,y1-y0)*0.05
    title=f'TESTDATEN · {channel.face.value} {channel.direction.value} · kein Ausführungsplan'
    maximum=max((c.required[channel] for c in cells),default=1) or 1
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-margin} {y0-margin} {x1-x0+2*margin} {y1-y0+2*margin}" role="img">',f'<title>{escape(title)}</title>',
         f'<rect x="{x0-margin}" y="{y0-margin}" width="{x1-x0+2*margin}" height="{y1-y0+2*margin}" fill="white"/>',
         f'<text x="{x0}" y="{y0-margin/3}" font-size="110" fill="#172d3d">{escape(title)}</text>',
         f'<g transform="translate(0,{y0+y1}) scale(1,-1)">',
         f'<path d="{polygon_path(slab.footprint)}" fill="#f2f4f5" fill-rule="evenodd" stroke="#172d3d" stroke-width="16"/>']
    for c in cells:
        required=c.required[channel]
        light=95-55*required/maximum
        out.append(f'<path d="{polygon_path(c.polygon)}" fill="hsl(205,65%,{light:g}%)" stroke="#326481" stroke-width="8"><title>{escape(c.id)}: As erforderlich {required:g} cm²/m</title></path>')
    for p in proposals:
        if p.region.channel!=channel: continue
        for b in p.bars:
            a,z=b.coords[0],b.coords[-1]
            out.append(f'<path d="M {a[0]},{a[1]} L {z[0]},{z[1]}" stroke="#a14215" stroke-width="12"><title>Ø{p.spec.diameter:g}/{p.spec.spacing:g} mm; As {p.spec.area:.2f} cm²/m</title></path>')
    out.extend(['</g>','</svg>'])
    return '\n'.join(out)
