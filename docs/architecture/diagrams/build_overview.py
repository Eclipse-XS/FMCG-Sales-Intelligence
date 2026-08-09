"""Build editable Draw.io XML and export its simple shape subset to SVG/PNG.

Run from the repository root with the project Python (Pillow required for PNG).
The preview reads the saved XML; it is not a diagrams.net application export.
"""
from pathlib import Path
import math
import xml.etree.ElementTree as ET
from html import escape
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
W, H = 1760, 1100
doc = ET.Element('mxfile', host='app.diagrams.net', version='26.0.0')
diagram = ET.SubElement(doc, 'diagram', id='fmcg-overview', name='System Architecture')
graph = ET.SubElement(diagram, 'mxGraphModel', dx=str(W), dy=str(H), grid='1', gridSize='10', page='1', pageScale='1', pageWidth=str(W), pageHeight=str(H), background='#FFFFFF', arrows='1', connect='1')
root = ET.SubElement(graph, 'root')
ET.SubElement(root, 'mxCell', id='0')
ET.SubElement(root, 'mxCell', id='1', parent='0')
colors = {'source':'#F0F3F5','data':'#EAF2FA','ml':'#F0EBF8','product':'#EAF4EE','infra':'#FBF1E5','plain':'#FFFFFF'}
boxes = {}
routes = []

def shape(id, x, y, w, h, text='', kind='plain', size=19, bold=False, border=True):
    style = f'rounded=0;whiteSpace=wrap;html=0;fillColor={colors[kind] if border else "none"};strokeColor={"#81909F" if border else "none"};fontColor=#203044;fontFamily=Arial;fontSize={size};fontStyle={1 if bold else 0};align=center;verticalAlign=middle;spacing=6;'
    cell=ET.SubElement(root,'mxCell',id=id,value=text,style=style,vertex='1',parent='1')
    ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
    if border: boxes[id]=(x,y,w,h)
    return id

def block(id,x,y,w,h,title,body,kind='plain',size=19):
    shape(id,x,y,w,h,kind=kind)
    shape(id+'-title',x+5,y+9,w-10,48,title,size=size,bold=True,border=False)
    if body: shape(id+'-body',x+7,y+60,w-14,h-69,body,size=18,border=False)

def edge(id,source,target,points,dashed=False):
    sx,sy,sw,sh=boxes[source]; tx,ty,tw,th=boxes[target]
    a,b=points[0],points[-1]
    style=f'edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;endFill=1;strokeColor=#52677B;strokeWidth={1.5 if dashed else 2};dashed={1 if dashed else 0};exitX={(a[0]-sx)/sw};exitY={(a[1]-sy)/sh};exitPerimeter=0;entryX={(b[0]-tx)/tw};entryY={(b[1]-ty)/th};entryPerimeter=0;'
    c=ET.SubElement(root,'mxCell',id=id,style=style,edge='1',parent='1',source=source,target=target)
    g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
    arr=ET.SubElement(g,'Array',attrib={'as':'points'})
    for x,y in points[1:-1]: ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
    routes.append((id,source,target,points))

shape('title',30,22,1700,50,'FMCG Sales Intelligence — System Architecture',size=32,bold=True,border=False)
shape('subtitle',30,78,1700,32,'Local academic platform • Generic FMCG core • Frozen scientific V1 / runtime V1.3',size=21,border=False)
for id,x,w,text in [('sources',30,220,'01  Sources &\nconfiguration'),('ingestion',275,175,'02  Ingestion &\ndata quality'),('operational',475,180,'03  Operational\ndata layer'),('analytical',680,215,'04  Analytical\ndata layer'),('science',920,300,'05  ML & analytics'),('serving',1245,230,'06  Serving &\nproduct'),('presentation',1500,230,'07  Presentation')]:
    shape('heading-'+id,x,134,w,55,text,size=21,bold=True,border=False)

block('public',30,235,220,118,'Public retail data','Reference / donor\ncalibration','source')
block('synthetic',30,390,220,115,'Synthetic FMCG','Generated canonical\nCSV data','source')
block('config',30,548,220,165,'Domain & contracts','Replaceable pack\ncoca_cola_demo\nconfig/domains\nconfig/contracts','source')
block('ingest',275,390,175,220,'Python pipelines','Ingest / load\nMapping adapters\nContract checks\nGenerated-data &\nDB validation','source')
block('pg',475,390,180,220,'PostgreSQL','Operational\nfmcg schema\nSales / inventory\nOrders / deliveries\nProducts / stores','data')
block('warehouse',680,390,215,142,'DuckDB + dbt','Staging / marts\nExtraction + dbt tests','data')
block('datasets',680,575,215,126,'Processed datasets','Task-specific Parquet\nPolars + GE checks','data')

shape('ml',920,235,300,370,kind='ml')
shape('ml-title',928,245,284,40,'Seven scientific cores',size=21,bold=True,border=False)
for i,(id,text) in enumerate([('forecast','Demand\nForecasting'),('stockout','Stockout\nClassification'),('survival','Stockout\nSurvival'),('segment','Store\nSegmentation'),('anomaly','Anomaly\nDetection'),('basket','Market Basket\nAnalysis')]):
    shape('core-'+id,930+(i%2)*145,298+(i//2)*71,135,61,text,kind='ml',size=18)
shape('core-promotion',930,511,280,46,'Promotion Analysis',kind='ml',size=18)
shape('ml-note',930,562,280,35,'Independent task pipelines',size=18,border=False)
block('artifacts',920,648,300,105,'Frozen canonical artifacts','Models • outputs • metrics','ml')

block('api',1245,390,230,363,'FastAPI','Request validation\nFrozen artifact loading\n\nForecast / stockout risk\nExperimental frozen\nKMeans membership\n\nOffline analytical outputs\nWarehouse KPIs','product')
block('dashboard',1500,390,230,185,'Grafana Dashboards','PostgreSQL + Prometheus\n11 Dashboards-as-Code\n\nBusiness & ML Analytics','product')

edge('donors','public','synthetic',[(140,353),(140,390)])
edge('batch','synthetic','ingest',[(250,445),(275,445)])
edge('configuration','config','ingest',[(250,585),(275,585)],True)
edge('load','ingest','pg',[(450,445),(475,445)])
edge('extract','pg','warehouse',[(655,445),(680,445)])
edge('build','warehouse','datasets',[(785,532),(785,575)])
edge('model-input','datasets','ml',[(895,592),(920,592)])
edge('persist','ml','artifacts',[(1070,605),(1070,648)])
edge('load-frozen','artifacts','api',[(1220,700),(1245,700)])
edge('responses','api','dashboard',[(1475,460),(1500,460)])
edge('bi','warehouse','api',[(790,390),(790,210),(1360,210),(1360,390)])
shape('bi-label',890,188,360,22,'Read-only warehouse → BI / KPIs',size=18,border=False)
shape('api-ui-label',1480,590,260,54,'HTTP / JSON responses',size=18,border=False)

block('replay',475,657,180,118,'Isolated replay','PostgreSQL\nstreaming schema','data')
block('kafka',30,832,220,146,'Kafka / Kafka UI','Optional local replay\nValidated consumer\nIdempotency + DLQ','infra')
edge('replay-write','kafka','replay',[(140,832),(140,800),(565,800),(565,775)],True)
block('airflow',275,832,380,146,'Apache Airflow — bounded local demo','Executed: frozen-evidence smoke check\nDefined batch DAG: DB validation → extract\n→ dbt → dataset build → quality checks','infra')
edge('airflow-defined','airflow','datasets',[(655,895),(665,895),(665,735),(760,735),(760,701)],True)
block('dvc',680,832,215,146,'DVC','Data / dependencies\nArtifacts / metrics\nGoogle Drive remote','infra')
edge('dvc-data','dvc','datasets',[(805,832),(805,701)],True)
edge('dvc-artifact','dvc','artifacts',[(895,870),(908,870),(908,783),(950,783),(950,753)],True)
block('mlflow',920,832,300,146,'MLflow','Canonical run metadata\nModel registry / serving aliases\nOutside request execution','infra')
edge('tracking','artifacts','mlflow',[(1100,753),(1100,832)],True)
block('prometheus',1245,832,230,146,'Prometheus','Scrapes FastAPI\n/metrics\nOperational telemetry','infra')
edge('scrape','prometheus','api',[(1360,832),(1360,753)],True)
block('grafana',1500,832,230,146,'Grafana','Prometheus datasource\nAlso: PostgreSQL\noperational datasource','infra')
edge('telemetry','prometheus','grafana',[(1475,890),(1500,890)],True)

shape('runtime',30,1000,1700,42,'Docker Compose local services: PostgreSQL • FastAPI • Dashboard • MLflow • Prometheus • Grafana • Kafka / Kafka UI',kind='infra',size=19)
shape('legend',30,1052,1700,28,'Solid arrows: data / result flow     |     Dashed: configuration, optional replay, control, versioning, metadata, monitoring     |     Airflow: separate ephemeral runtime',size=18,border=False)
# Keep component labels and scientific cores attached when moving their parent.
for c in list(root):
    id=c.get('id',''); parent=None
    if id.endswith(('-title','-body')) and id.rsplit('-',1)[0] in boxes:
        parent=id.rsplit('-',1)[0]
    if id.startswith('core-') or id=='ml-note': parent='ml'
    if parent:
        c.set('parent',parent); g=c.find('mxGeometry'); px,py,_,_=boxes[parent]
        g.set('x',str(float(g.get('x'))-px)); g.set('y',str(float(g.get('y'))-py))
ET.indent(doc)
file=OUT/'fmcg_system_architecture.drawio'
ET.ElementTree(doc).write(file,encoding='utf-8',xml_declaration=True)

# Validate the saved editable document and export its plain rectangular subset.
cells=ET.parse(file).findall('.//mxCell'); ids=[c.get('id') for c in cells]
assert len(ids)==len(set(ids))
for c in cells:
    for ref in ('parent','source','target'):
        assert c.get(ref) is None or c.get(ref) in ids
    for g in c.findall('.//mxGeometry')+c.findall('.//mxPoint'):
        for attr in ('x','y','width','height'):
            if attr in g.attrib: assert math.isfinite(float(g.get(attr)))
for a,(x,y,w,h) in boxes.items():
    for b,(xx,yy,ww,hh) in boxes.items():
        if a>=b or a=='ml' or b=='ml': continue
        assert not (x<xx+ww and x+w>xx and y<yy+hh and y+h>yy), (a,b)
for id,source,target,pts in routes:
    for (x,y),(xx,yy) in zip(pts,pts[1:]):
        assert x==xx or y==yy, id
        for b,(bx,by,bw,bh) in boxes.items():
            if b in (source,target) or b.startswith('core-'): continue
            crosses=(bx<x<bx+bw and max(min(y,yy),by)<min(max(y,yy),by+bh)) if x==xx else (by<y<by+bh and max(min(x,xx),bx)<min(max(x,xx),bx+bw))
            assert not crosses,(id,b)

scale=2
im=Image.new('RGB',(W*scale,H*scale),'white'); d=ImageDraw.Draw(im)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>']
fontroot=Path('C:/Windows/Fonts')
def line(a,b,color,width=2,dashed=False):
    x,y=a; xx,yy=b
    if dashed:
        length=math.dist(a,b)
        for t in range(0,int(length),12):
            end=min(t+7,length)
            d.line(((x+(xx-x)*t/length)*scale,(y+(yy-y)*t/length)*scale,(x+(xx-x)*end/length)*scale,(y+(yy-y)*end/length)*scale),fill=color,width=max(1,int(width*scale)))
    else:d.line((x*scale,y*scale,xx*scale,yy*scale),fill=color,width=int(width*scale))

for c in cells:
    if c.get('vertex')!='1': continue
    s=dict(v.split('=',1) for v in c.get('style').split(';') if '=' in v)
    g=c.find('mxGeometry'); x,y,w,h=[float(g.get(k)) for k in ('x','y','width','height')]
    parent=c.get('parent')
    if parent in boxes:
        px,py,_,_=boxes[parent]; x+=px; y+=py
    fill,stroke=s['fillColor'],s['strokeColor']
    if fill!='none':
        d.rectangle((x*scale,y*scale,(x+w)*scale,(y+h)*scale),fill=fill,outline=stroke,width=2)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>')
    text=c.get('value','')
    if not text: continue
    size=int(s['fontSize']); bold=s['fontStyle']=='1'; font=ImageFont.truetype(str(fontroot/('arialbd.ttf' if bold else 'arial.ttf')),size*scale)
    lines=text.split('\n'); step=size*1.2
    assert len(lines)*step<=h+1,(c.get('id'),'text height')
    for i,t in enumerate(lines):
        assert d.textlength(t,font=font)/scale <= w-8,(c.get('id'),'text width',t)
        cy=y+h/2+(i-(len(lines)-1)/2)*step
        d.text(((x+w/2)*scale,cy*scale),t,fill='#203044',font=font,anchor='mm')
        svg.append(f'<text x="{x+w/2}" y="{cy}" text-anchor="middle" dominant-baseline="central" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="#203044">{escape(t)}</text>')
for id,source,target,pts in routes:
    c=next(c for c in cells if c.get('id')==id); dashed='dashed=1;' in c.get('style'); color='#52677B'
    svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{color}" stroke-width="{1.5 if dashed else 2}"'+(' stroke-dasharray="7 5"' if dashed else '')+'/>')
    for a,b in zip(pts,pts[1:]):line(a,b,color,1.5 if dashed else 2,dashed)
    (x,y),(xx,yy)=pts[-2:]; angle=math.atan2(yy-y,xx-x)
    tip=[(xx,yy),(xx-10*math.cos(angle)+4*math.sin(angle),yy-10*math.sin(angle)-4*math.cos(angle)),(xx-10*math.cos(angle)-4*math.sin(angle),yy-10*math.sin(angle)+4*math.cos(angle))]
    d.polygon([(a*scale,b*scale) for a,b in tip],fill=color)
    svg.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in tip)}" fill="{color}"/>')
svg.append('</svg>')
(OUT/'fmcg_system_architecture.svg').write_text('\n'.join(svg),encoding='utf-8')
im.save(OUT/'fmcg_system_architecture.png',dpi=(300,300))
print(f'Validated: {len(ids)} unique cells; {len(routes)} orthogonal connectors; finite coordinates; no major-box overlap or unrelated-box crossings; text fits. SVG/PNG exported from XML.')





