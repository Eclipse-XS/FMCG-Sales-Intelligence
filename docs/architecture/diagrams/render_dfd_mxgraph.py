"""Import the saved Draw.io XML with mxGraph and render all four pages locally.

Requires an existing mxgraph/javascript/dist/build.js and Chromium/Chrome.
No runtime/application modules are imported. The browser uses a temporary profile.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
SVG = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG)
ET.register_namespace('xlink', XLINK)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mxgraph-js', type=Path, required=True)
    parser.add_argument('--chrome', type=Path, default=Path('C:/Program Files/Google/Chrome/Application/chrome.exe'))
    args = parser.parse_args()
    assert args.mxgraph_js.is_file() and args.chrome.is_file()
    source = BASE / 'fmcg_dfd.drawio'
    pages = ET.parse(source).findall('diagram')
    assert len(pages) == 4
    checks = []
    with tempfile.TemporaryDirectory(prefix='fmcg-dfd-check-') as temp:
        work = Path(temp)
        for page in pages:
            slug = page.get('id')
            model = page.find('mxGraphModel')
            width, height = int(model.get('pageWidth')), int(model.get('pageHeight'))
            xml = ET.tostring(model, encoding='unicode')
            html = (
                '<!doctype html><html><head><meta charset="utf-8">'
                '<style>html,body{margin:0;background:white;overflow:hidden}'
                f'#graph{{width:{width}px;height:{height}px;position:relative}}</style>'
                f'<script src="{args.mxgraph_js.resolve().as_uri()}"></script></head>'
                '<body><div id="graph"></div><pre id="check" style="display:none"></pre>'
                '<script>try{Object.assign(window,mxgraph({mxLoadResources:false,mxLoadStylesheets:false}));'
                'const graph=new mxGraph(document.getElementById("graph"));graph.setEnabled(false);'
                'graph.foldingEnabled=false;'
                f'const xml=mxUtils.parseXml({json.dumps(xml)});'
                'new mxCodec(xml).decode(xml.documentElement,graph.getModel());'
                'graph.refresh();graph.view.validate();'
                'document.getElementById("check").textContent="IMPORT_PASS:"+Object.keys(graph.model.cells).length;'
                '}catch(e){document.getElementById("check").textContent="IMPORT_FAIL:"+e.stack;}'
                '</script></body></html>'
            )
            path = work / f'{slug}.html'
            path.write_text(html, encoding='utf-8')
            png = BASE / 'previews' / f'{slug}.png'
            result = subprocess.run([
                str(args.chrome), '--headless', '--disable-gpu', '--no-first-run',
                '--no-default-browser-check', '--disable-extensions',
                '--allow-file-access-from-files', '--hide-scrollbars',
                f'--window-size={width},{height}', '--force-device-scale-factor=2',
                '--virtual-time-budget=1500', f'--user-data-dir={work / "profile"}',
                f'--screenshot={png}', '--dump-dom', path.as_uri(),
            ], capture_output=True, encoding='utf-8', errors='replace', timeout=45)
            check = re.search(r'<pre id="check"[^>]*>IMPORT_PASS:(\d+)</pre>', result.stdout)
            assert result.returncode == 0 and check, (slug, 'mxGraph import failed', result.stdout[-1000:])
            count = int(check.group(1))
            assert count == len(model.findall('.//mxCell')), (slug, 'cell count mismatch')
            native = re.search(r'<svg\b[\s\S]*?</svg>', result.stdout).group(0)
            native = native.replace('<svg ', f'<svg xmlns="{SVG}" xmlns:xlink="{XLINK}" ', 1)
            svg = ET.fromstring(native)
            svg.attrib.pop('style', None)
            svg.set('width', str(width)); svg.set('height', str(height))
            svg.set('viewBox', f'0 0 {width} {height}')
            svg.insert(0, ET.Element(f'{{{SVG}}}rect', width='100%', height='100%', fill='white'))
            assert not svg.findall(f'.//{{{SVG}}}image'), (slug, 'unexpected image/UI icon')
            ET.ElementTree(svg).write(BASE / 'previews' / f'{slug}.svg', encoding='utf-8', xml_declaration=True)
            checks.append({'page':page.get('name'), 'import':'PASS', 'cells':count})
            print(f'{slug}: mxGraph import PASS ({count} cells); native SVG/PNG exported')
    report_path = BASE / 'fmcg_dfd_validation.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    report.update(mxgraph_import='PASS', mxgraph_version='4.2.2', native_pages=checks,
                  preview_method='mxGraph SVG / headless Chrome PNG',
                  drawio_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
