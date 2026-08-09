"""Reapply and verify the reviewed geometry without regenerating either model."""
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from refine_erd_layout import ExistingDiagram, box, geometry_metrics, overlap, style

BASE = Path(__file__).resolve().parent
VISUAL_EDGE_KEYS = {'exitX', 'exitY', 'entryX', 'entryY', 'strokeColor', 'strokeWidth'}


def validate_pair(kind, before, after):
    old = {c.get('id'): c for c in before.findall('.//mxCell')}
    new = {c.get('id'): c for c in after.findall('.//mxCell')}
    assert set(old) == set(new), 'Cell IDs/count changed'
    for cid, c in new.items():
        original = old[cid]
        a, b = dict(original.attrib), dict(c.attrib)
        if c.get('edge') == '1':
            a.pop('style'); b.pop('style')
            assert {k: v for k, v in style(original).items() if k not in VISUAL_EDGE_KEYS} == {
                k: v for k, v in style(c).items() if k not in VISUAL_EDGE_KEYS}
            if kind == 'physical':
                for anchor in ('exitY', 'entryY'):
                    assert abs(float(style(original)[anchor])-float(style(c)[anchor])) < 1e-9, (cid, anchor)
        assert a == b, (cid, 'text or metadata changed')
        if c.get('edge') != '1':
            g, h = original.find('mxGeometry'), c.find('mxGeometry')
            if g is not None:
                assert {k: v for k, v in g.attrib.items() if k not in ('x', 'y')} == {
                    k: v for k, v in h.attrib.items() if k not in ('x', 'y')}, cid
        for key in ('parent', 'source', 'target'):
            assert not c.get(key) or c.get(key) in new, (cid, 'dangling reference')
    nodes = {i: box(c) for i, c in new.items() if c.get('entity')}
    labels = {i: box(c) for i, c in new.items() if c.get('parent') == '1' and c.get('value') in {'1', '0..1', '0..N'}}
    routes = {}; original_routes = {}
    for cid, e in new.items():
        if e.get('edge') != '1': continue
        def read(edge, cells):
            st = style(edge); ends = []
            for attr, pre in [('source', 'exit'), ('target', 'entry')]:
                x, y, w, h = box(cells[edge.get(attr)])
                ends.append((round(x+w*float(st[pre+'X']), 6), round(y+h*float(st[pre+'Y']), 6)))
            return [ends[0]] + [(float(p.get('x')), float(p.get('y'))) for p in edge.findall('.//mxPoint')] + [ends[1]]
        routes[cid] = read(e, new); original_routes[cid] = read(old[cid], old)
    metrics = geometry_metrics(nodes, routes, labels)
    # A shared lead with the same entity/cardinality is a fan-out. Other T-joins
    # or coincident segments would look like relationships not present in XML.
    touches=set();coincident=0
    ids=list(routes)
    for i,eid in enumerate(ids):
        e=new[eid]
        ends={(e.get('source'),e.get('sourceCardinality')),(e.get('target'),e.get('targetCardinality'))}
        for oid in ids[i+1:]:
            o=new[oid]
            if ends & {(o.get('source'),o.get('sourceCardinality')),(o.get('target'),o.get('targetCardinality'))}:continue
            for a,b in zip(routes[eid],routes[eid][1:]):
                for c,d in zip(routes[oid],routes[oid][1:]):
                    for u,v,r,s in [(a,b,c,d),(c,d,a,b)]:
                        if u[0]==v[0] and r[1]==s[1] and min(r[0],s[0])<=u[0]<=max(r[0],s[0]) and min(u[1],v[1])<=r[1]<=max(u[1],v[1]):
                            if not(min(r[0],s[0])<u[0]<max(r[0],s[0]) and min(u[1],v[1])<r[1]<max(u[1],v[1])):touches.add((eid,oid,u[0],r[1]))
                    if a[0]==b[0]==c[0]==d[0]:coincident+=max(0,min(max(a[1],b[1]),max(c[1],d[1]))-max(min(a[1],b[1]),min(c[1],d[1])))
                    if a[1]==b[1]==c[1]==d[1]:coincident+=max(0,min(max(a[0],b[0]),max(c[0],d[0]))-max(min(a[0],b[0]),min(c[0],d[0])))
    metrics['ambiguous_T_joins']=sorted(touches)
    metrics['unrelated_coincident_segment_length']=coincident
    assert not touches and coincident==0,('ambiguous connector joins',touches,coincident)
    for key in ['box_overlaps', 'label_overlaps', 'label_box_overlaps', 'connectors_through_boxes', 'connectors_through_labels']:
        assert not metrics[key], (key, metrics[key])
    annotations = [(cid, box(c)) for cid, c in new.items() if c.get('parent') == '1' and c.get('vertex') == '1' and not c.get('entity')]
    for i, (cid, r) in enumerate(annotations):
        assert all(not overlap(r, s) for other, s in annotations[i+1:]), ('annotation overlap', cid)
        assert all(not overlap(r, s) for s in nodes.values()), ('annotation/table overlap', cid)
    page = after.find('.//mxGraphModel')
    for c in new.values():
        if c.get('parent') == '1' and c.get('vertex') == '1':
            x, y, w, h = box(c)
            assert x >= 0 and y >= 0 and x+w <= float(page.get('pageWidth')) and y+h <= float(page.get('pageHeight')), ('canvas bounds', c.get('id'))
    before_metrics = ExistingDiagram(kind).before
    return {'entities_before_after': [len(nodes), len(nodes)], 'edges_before_after': [len(routes), len(routes)],
            'native_cells_before_after': [len(old), len(new)],
            'names_fields_types_PK_FK_UNIQUE_nullability_cardinality_relationship_metadata': 'IDENTICAL',
            'all_vertex_text_styles_fonts_widths_heights': 'IDENTICAL',
            'physical_FK_PK_row_offsets': 'IDENTICAL' if kind == 'physical' else 'not applicable',
            'xml_parse': 'PASS', 'dangling_references': 0,
            'edges_rerouted': sum(routes[i] != original_routes[i] for i in routes),
            'old_waypoints_replaced': sum(len(p)-2 for p in original_routes.values()),
            'new_waypoints': sum(len(p)-2 for p in routes.values()),
            'page': [int(page.get('pageWidth')), int(page.get('pageHeight'))],
            'before': before_metrics, 'after': metrics}


def main():
    manifest = json.loads((BASE / 'readable_v2_geometry.json').read_text(encoding='utf-8'))
    report = {}
    for kind, layout in manifest.items():
        source = BASE / f'fmcg_{kind}_erd.drawio'
        assert hashlib.sha256(source.read_bytes()).hexdigest() == layout['source_sha256'], 'Source changed: review the layout again'
        original = ET.parse(source); document = copy.deepcopy(original)
        model = document.find('.//mxGraphModel')
        for key, value in layout['page'].items(): model.set(key, value)
        cells = {c.get('id'): c for c in document.findall('.//mxCell')}
        for cid, update in layout['cells'].items():
            c = cells[cid]
            c.remove(c.find('mxGeometry')); c.append(ET.fromstring(update['geometry']))
            if 'edge_style' in update: c.set('style', update['edge_style'])
        output = BASE / f'fmcg_{kind}_erd_readable_v2.drawio'
        checks = validate_pair(kind, original, document)
        ET.indent(document); document.write(output, encoding='utf-8', xml_declaration=True)
        ET.parse(output)
        checks.update(input=str(source), output=str(output), source_sha256=layout['source_sha256'],
                      output_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
        report[kind] = checks
        print(kind, 'PASS', 'crossings', checks['before']['crossings'], '->', checks['after']['crossings'])
    (BASE / 'fmcg_readable_v2_validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__': main()
