"""Independently compare saved native diagram rows and edges with parsed DDL."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from audit_schema import audit

BASE = Path(__file__).resolve().parent


def verify():
    model = audit()
    root = ET.parse(BASE / 'fmcg_physical_erd.drawio')
    cells = root.findall('.//mxCell')
    frames = {c.get('entity'): c for c in cells if c.get('entity')}
    assert set(frames) == set(model['tables'])
    entity_by_id = {c.get('id'): name for name, c in frames.items()}
    for name, table in model['tables'].items():
        rows = {}
        for c in cells:
            if c.get('parent') != frames[name].get('id'):
                continue
            g = c.find('mxGeometry')
            x, y = float(g.get('x', 0)), float(g.get('y', 0))
            if x in (8, 94, 442, 610):
                rows.setdefault(y, {})[x] = c.get('value', '')
        actual = [rows[y] for y in sorted(rows)]
        assert len(actual) == len(table['columns']), name
        for row, col in zip(actual, table['columns']):
            marks = []
            if col['name'] in table['primary_key']:
                marks.append('PK')
            if any(f['column'] == col['name'] for f in table['foreign_keys']):
                marks.append('FK')
            marks.extend('U' + str(i + 1) for i, u in enumerate(table['unique']) if col['name'] in u)
            if col['generated_stored']:
                marks.append('G')
            assert row == {8: '/'.join(marks), 94: col['name'], 442: col['type'],
                           610: 'NL' if col['nullable'] else 'NN'}, (name, col['name'])
    expected = {(n, f['column'], f['parent'], f['parent_column'], f['child_end'], f['parent_end'])
                for n, t in model['tables'].items() for f in t['foreign_keys']}
    edges = [c for c in cells if c.get('edge') == '1']
    actual = {(entity_by_id[c.get('source')], c.get('foreignKey'), entity_by_id[c.get('target')],
               c.get('referencedColumn'), c.get('sourceCardinality'), c.get('targetCardinality')) for c in edges}
    assert len(edges) == len(expected) == 29 and actual == expected
    for edge in edges:
        style = dict(p.split('=', 1) for p in edge.get('style').split(';') if '=' in p)
        for side, field, anchor in [('source', 'foreignKey', 'exit'), ('target', 'referencedColumn', 'entry')]:
            entity = entity_by_id[edge.get(side)]
            columns = model['tables'][entity]['columns']
            index = next(i for i, c in enumerate(columns) if c['name'] == edge.get(field))
            height = float(frames[entity].find('mxGeometry').get('height'))
            assert abs(float(style[anchor + 'Y']) * height - (42 + index * 27 + 13.5)) < 1e-6
    logical = ET.parse(BASE / 'fmcg_logical_erd.drawio').findall('.//mxCell')
    assert sum(bool(c.get('entity')) for c in logical) == 16
    assert sum(c.get('edge') == '1' for c in logical) == 27
    for c in cells + logical:
        assert 'image=' not in c.get('style', '') and 'html=1' not in c.get('style', '')
    path = BASE / 'fmcg_erd_validation.json'
    report = json.loads(path.read_text())
    report['saved_xml_against_DDL'] = {
        'all_146_column_names_types_keys_nullability': 'PASS',
        'all_29_FK_targets_and_min_max_cardinalities': 'PASS',
        'all_29_connectors_anchor_at_FK_and_PK_row_centers': 'PASS',
        'native_editable_shapes_without_embedded_images_or_HTML': 'PASS'}
    path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report['saved_xml_against_DDL'], indent=2))


if __name__ == '__main__':
    verify()
