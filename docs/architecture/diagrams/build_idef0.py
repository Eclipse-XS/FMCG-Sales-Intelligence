"""Documentation-only IDEF0 source, semantic checks, and XML-based previews.

Run with the project Python. Pillow is used only to render diagram primitives.
No application modules are imported and no scientific/runtime state is touched.
"""
from pathlib import Path
from html import escape
import json
import math
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
PREVIEW = OUT / 'previews'
W, H = 1840, 1160
DOC = ET.Element('mxfile', host='app.diagrams.net', version='26.0.0')
PAGES = []


class Page:
    def __init__(self, node, title, slug, note=''):
        self.node, self.slug = node, slug
        self.boxes, self.routes, self.ports, self.boundary = {}, [], {}, {}
        self.count = 0
        dg = ET.SubElement(DOC, 'diagram', id=slug, name=f'{node} — {title}')
        gm = ET.SubElement(dg, 'mxGraphModel', dx=str(W), dy=str(H), grid='1', gridSize='10', page='1', pageWidth=str(W), pageHeight=str(H), pageScale='1', background='#FFFFFF')
        self.root = ET.SubElement(gm, 'root')
        ET.SubElement(self.root, 'mxCell', id=f'{slug}-0')
        ET.SubElement(self.root, 'mxCell', id=f'{slug}-1', parent=f'{slug}-0')
        self.base = f'{slug}-1'
        # Page titles live in Draw.io tabs; the canvas follows the plain references.
        PAGES.append(self)

    def cell(self, value, x, y, w, h, style, parent=None, name=None, **attrs):
        self.count += 1
        id = name or f'{self.slug}-v{self.count}'
        c = ET.SubElement(self.root, 'mxCell', id=id, value=value, style=style, vertex='1', parent=parent or self.base, **attrs)
        ET.SubElement(c, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), attrib={'as':'geometry'})
        return id

    def text(self, x, y, w, h, value, size=20, bold=False, parent=None, align='center', inline=False):
        fill='#FFFFFF' if inline else 'none'
        return self.cell(value,x,y,w,h,f'text;html=0;whiteSpace=wrap;fillColor={fill};strokeColor=none;fontColor=#000000;fontFamily=Arial;fontSize={size};fontStyle={1 if bold else 0};align={align};verticalAlign=middle;spacing=0;',parent=parent,inlineLabel='1' if inline else '0')

    def box(self, node, x, y, w, h, title):
        id=f'{self.slug}-{node}'
        self.cell('',x,y,w,h,'rounded=0;html=0;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.2;container=1;collapsible=0;',name=id,function=node)
        self.text(10,32,w-20,h-40,title,20,False,parent=id)
        self.text(7,5,80,25,node,19,False,parent=id,align='left')
        self.boxes[node]=(x,y,w,h,id)
        self.ports[node]={k:set() for k in 'ICOM'}

    def junction(self,x,y):
        return self.cell('',x-2,y-2,4,4,'ellipse;fillColor=#000000;strokeColor=none;')

    def arrow(self, points, *, source=None, target=None, role=None, flow=None, boundary=None, head=True):
        self.count+=1
        id=f'{self.slug}-e{self.count}'
        attr={'semanticFlow':flow or '', 'icomRole':role or ''}
        style='edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;strokeColor=#000000;strokeWidth=1.2;jumpStyle=arc;jumpSize=7;endArrow='+('block' if head else 'none')+';endFill=1;'
        for key,node,point in [('source',source,points[0]),('target',target,points[-1])]:
            if node:
                x,y,w,h,cell=self.boxes[node]
                attr[key]=cell
                prefix='exit' if key=='source' else 'entry'
                style+=f'{prefix}X={(point[0]-x)/w};{prefix}Y={(point[1]-y)/h};{prefix}Perimeter=0;'
        if source: self.ports[source]['O'].add(flow)
        if target:
            assert role in 'ICM'
            self.ports[target][role].add(flow)
        if boundary:
            kind,code=boundary
            assert (code not in self.boundary) or self.boundary[code]==(kind,flow)
            self.boundary[code]=(kind,flow)
            attr.update(boundaryCode=code,boundaryRole=kind)
        c=ET.SubElement(self.root,'mxCell',id=id,style=style,edge='1',parent=self.base,**attr)
        g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
        ET.SubElement(g,'mxPoint',x=str(points[0][0]),y=str(points[0][1]),attrib={'as':'sourcePoint'})
        ET.SubElement(g,'mxPoint',x=str(points[-1][0]),y=str(points[-1][1]),attrib={'as':'targetPoint'})
        arr=ET.SubElement(g,'Array',attrib={'as':'points'})
        for x,y in points[1:-1]: ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        self.routes.append(dict(id=id,points=points,source=source,target=target,role=role,flow=flow,head=head))


def bundle(page, flow, code, role, source_x, lane_y, targets, label, label_x, label_y, label_w=240, label_h=75):
    """One external resource/rule with selectively routed branches."""
    start_y=25 if role=='C' else 1120
    page.arrow([(source_x,start_y),(source_x,lane_y)],flow=flow,boundary=(role,code),head=False)
    xs=[x for node,x in targets]+[source_x]
    if min(xs)!=max(xs):
        page.arrow([(min(xs),lane_y),(max(xs),lane_y)],flow=flow,head=False)
        page.junction(source_x,lane_y)
    for node,x in targets:
        bx,by,bw,bh,_=page.boxes[node]
        end_y=by if role=='C' else by+bh
        page.arrow([(x,lane_y),(x,end_y)],target=node,role=role,flow=flow)
        if min(xs)!=max(xs):page.junction(x,lane_y)
    page.text(label_x,label_y,label_w,label_h,label,19,inline=True)


# Existing functions and data dependencies are retained; only their presentation
# and the old aggregate rule/resource bundles are refined.
ctx=Page('A-0','Контекстна діаграма','idef0_a_minus_0')
ctx.box('A0',620,400,600,270,'Обробляти FMCG-дані,\nформувати аналітичні результати\nта надавати їх користувачам')
ctx.arrow([(70,475),(620,475)],target='A0',role='I',flow='sources',boundary=('I','I1'))
ctx.text(115,422,455,48,'Операційні, довідкові та синтетичні\nFMCG-дані; донорські набори',20,inline=True)
ctx.arrow([(70,590),(620,590)],target='A0',role='I',flow='requests',boundary=('I','I2'))
ctx.text(125,532,445,52,'Запити та параметри отримання\nаналітичних результатів',20,inline=True)
for x,flow,code,label in [
    (700,'data_rules','C1','Контракти даних\nі правила якості'),
    (920,'method','C2','Методика ML\nта аналітичної обробки'),
    (1140,'execution','C3','Доменні правила\nта правила виконання')]:
    ctx.arrow([(x,100),(x,400)],target='A0',role='C',flow=flow,boundary=('C',code))
    ctx.text(x-108,215,216,80,label,19,inline=True)
for y,flow,code,label in [
    (435,'canonical','O1','Канонічні моделі, результати та метрики'),
    (505,'delivery','O2','Прогнози, ризики, KPI та відповіді API'),
    (575,'trace','O3','Версії артефактів і метадані запусків'),
    (645,'quality','O4','Звіти перевірок якості даних')]:
    ctx.arrow([(1220,y),(1770,y)],source='A0',flow=flow,boundary=('O',code))
    ctx.text(1270,y-29,450,24,label,20,inline=True)
for x,flow,code,label in [
    (670,'data_tools','M1','Сховища й засоби\nпідготовки даних'),
    (835,'ml_tools','M2','Модулі ML\nта аналітики'),
    (1000,'lifecycle_tools','M3','Засоби\nвідтворюваності'),
    (1165,'product_tools','M4','Програмна\nінфраструктура\nта інтерфейси')]:
    ctx.arrow([(x,1010),(x,670)],target='A0',role='M',flow=flow,boundary=('M',code))
    ctx.text(x-81,800,162,90,label,18,inline=True)


a0=Page('A0','Декомпозиція FMCG Sales Intelligence','idef0_a0')
for n,x,y,t in [
    ('A1',240,300,'Інтегрувати,\nперевіряти й\nзберігати дані'),
    ('A2',530,410,'Формувати\nаналітичні\nнабори даних'),
    ('A3',820,520,'Виконувати ML\nта аналітичну\nобробку даних'),
    ('A4',1110,630,'Версіонувати дані\nта реєструвати\nартефакти'),
    ('A5',1400,740,'Надавати прогнози\nта аналітичні\nрезультати')]:a0.box(n,x,y,210,135,t)

bundle(a0,'data_rules','C1','C',345,160,[('A1',310),('A2',600),('A5',1430)],'Контракти даних\nі правила якості',245,40,200,65)
bundle(a0,'method','C2','C',925,200,[('A3',930),('A5',1505)],'Методика ML\nта аналітичної обробки',815,40,220,65)
bundle(a0,'execution','C3','C',1215,110,[('A1',395),('A2',690),('A4',1215),('A5',1580)],'Доменні правила\nта правила виконання',1105,35,220,65)
bundle(a0,'data_tools','M1','M',170,1020,[('A1',295),('A2',585),('A5',1440)],'Сховища й засоби\nпідготовки даних',55,1040,230,65)
bundle(a0,'ml_tools','M2','M',875,970,[('A3',875),('A5',1505)],'Модулі ML\nта аналітики',765,1040,220,65)
bundle(a0,'lifecycle_tools','M3','M',1165,1000,[('A4',1165)],'Засоби\nвідтворюваності',1055,1040,220,65)
bundle(a0,'product_tools','M4','M',1560,1000,[('A5',1560)],'Програмна інфраструктура\nта інтерфейси',1430,1040,260,65)
a0.arrow([(65,370),(240,370)],target='A1',role='I',flow='sources',boundary=('I','I1'))
a0.text(65,297,165,67,'Дані FMCG\nта донорські\nнабори',19,inline=True)
a0.arrow([(450,370),(490,370),(490,480),(530,480)],source='A1',target='A2',role='I',flow='operational')
a0.text(453,385,73,57,'Факти',19,inline=True)
a0.arrow([(740,485),(780,485),(780,585),(820,585)],source='A2',target='A3',role='I',flow='datasets')
a0.text(742,492,77,54,'Набори\nданих',18,inline=True)
a0.junction(780,560)
a0.arrow([(780,560),(780,690),(1110,690)],target='A4',role='I',flow='datasets')
a0.text(900,655,150,28,'Набори даних',19)
a0.arrow([(740,445),(790,445),(790,390),(1370,390),(1370,785),(1400,785)],source='A2',target='A5',role='I',flow='marts')
a0.text(975,350,225,34,'Вітрини для KPI',19)
a0.arrow([(740,430),(765,430),(765,270),(1770,270)],source='A2',flow='quality',boundary=('O','O4'))
a0.text(1620,208,150,56,'Звіти перевірок\nякості даних',19,inline=True)
a0.arrow([(1030,585),(1770,585)],source='A3',flow='canonical',boundary=('O','O1'))
a0.text(1610,503,160,76,'Канонічні моделі,\nрезультати\nта метрики',19,inline=True)
a0.junction(1070,585)
a0.arrow([(1070,585),(1070,725),(1110,725)],target='A4',role='I',flow='canonical')
a0.junction(1345,585)
a0.arrow([(1345,585),(1345,825),(1400,825)],target='A5',role='I',flow='canonical')
a0.text(1075,532,110,48,'Збережені\nартефакти',19)
a0.arrow([(1320,690),(1770,690)],source='A4',flow='trace',boundary=('O','O3'))
a0.text(1610,621,160,62,'Версії та\nметадані запусків',19,inline=True)
a0.arrow([(65,930),(1365,930),(1365,852),(1400,852)],target='A5',role='I',flow='requests',boundary=('I','I2'))
a0.text(620,871,235,52,'Запити та параметри\nотримання результатів',19)
a0.arrow([(1610,805),(1770,805)],source='A5',flow='delivery',boundary=('O','O2'))
a0.text(1620,735,150,60,'Прогнози,\nKPI та відповіді',19,inline=True)


a2=Page('A2','Формування аналітичних наборів даних','idef0_a2')
for n,x,y,t in [
    ('A2.1',260,320,'Копіювати операційні\nфакти та довідники'),
    ('A2.2',620,430,'Перетворювати дані\nта перевіряти\nаналітичні вітрини'),
    ('A2.3',980,540,'Будувати ознаки,\nцілі та набори\nдля окремих задач'),
    ('A2.4',1340,650,'Перевіряти якість\nсформованих наборів')]:a2.box(n,x,y,250,145,t)
bundle(a2,'data_rules','C1','C',365,120,[('A2.1',365),('A2.2',735),('A2.3',1095),('A2.4',1455)],'Контракти даних\nі правила якості',245,35,240,65)
bundle(a2,'execution','C2','C',1050,190,[('A2.1',450),('A2.2',810),('A2.3',1170),('A2.4',1530)],'Правила виконання\nта конфігурація обробки',930,35,240,65)
bundle(a2,'data_tools','M1','M',720,990,[('A2.1',325),('A2.2',685),('A2.3',1045),('A2.4',1405)],'Сховища й засоби\nпідготовки даних',590,1030,260,70)
a2.arrow([(65,392),(260,392)],target='A2.1',role='I',flow='operational',boundary=('I','I1'))
a2.text(70,310,180,70,'Операційні факти\nта довідники',19,inline=True)
a2.arrow([(510,392),(565,392),(565,502),(620,502)],source='A2.1',target='A2.2',role='I',flow='raw')
a2.text(513,412,104,51,'Копія\nданих',19,inline=True)
a2.arrow([(870,502),(925,502),(925,612),(980,612)],source='A2.2',target='A2.3',role='I',flow='marts')
a2.text(925,430,150,48,'Аналітичні\nвітрини',19)
a2.junction(925,502)
a2.arrow([(925,502),(925,370),(1770,370)],flow='marts',boundary=('O','O2'))
a2.text(1600,310,170,52,'Вітрини\nдля KPI',19,inline=True)
a2.arrow([(1230,612),(1285,612),(1285,722),(1340,722)],source='A2.3',target='A2.4',role='I',flow='datasets')
a2.text(1290,553,100,50,'Записані\nнабори',19)
a2.junction(1285,612)
a2.arrow([(1285,612),(1285,480),(1770,480)],flow='datasets',boundary=('O','O1'))
a2.text(1600,415,170,52,'Набори даних\nдля задач',19,inline=True)
a2.arrow([(1590,722),(1770,722)],source='A2.4',flow='quality',boundary=('O','O3'))
a2.text(1598,630,170,82,'Звіт перевірок\nякості даних',19,inline=True)


a3=Page('A3','ML та аналітична обробка даних','idef0_a3')
branches=[
    ('A3.1',240,300,'Прогнозувати попит\nта оцінювати ризик\nдефіциту'),
    ('A3.2',530,410,'Аналізувати час\nдо дефіциту'),
    ('A3.3',820,520,'Виявляти сегменти\nта кандидатів\nв аномалії'),
    ('A3.4',1110,630,'Визначати асоціації\nта описувати\nпромоційні зміни')]
for n,x,y,t in branches:a3.box(n,x,y,210,135,t)
a3.box('A3.5',1400,740,210,135,'Зберігати моделі,\nрезультати\nта метрики задач')
bundle(a3,'method','C1','C',925,150,[(n,x+105) for n,x,y,t in branches]+[('A3.5',1505)],'Методика ML\nта аналітичної обробки',810,35,230,75)
bundle(a3,'ml_tools','M1','M',720,1030,[(n,x+55) for n,x,y,t in branches]+[('A3.5',1455)],'Модулі ML\nта аналітики',605,1050,230,60)
# Parallel task inputs remain independent despite the staircase arrangement.
a3.arrow([(65,245),(1070,245)],flow='datasets',boundary=('I','I1'),head=False)
a3.text(75,160,165,70,'Набори даних\nдля окремих\nзадач',19,inline=True)
for n,x,y,t in branches:
    ix=x-35 if n=='A3.1' else x-40 if n=='A3.4' else x-35
    a3.arrow([(ix,245),(ix,y+70),(x,y+70)],target=n,role='I',flow='datasets');a3.junction(ix,245)
# Results are a union of task outputs, never a sequential training chain.
for n,x,y,t in branches:
    ox=x+230 if n!='A3.4' else x+240
    a3.arrow([(x+210,y+70),(ox,y+70),(ox,910)],source=n,flow='task_results',head=False);a3.junction(ox,910)
a3.arrow([(470,910),(1375,910)],flow='task_results',head=False)
a3.arrow([(1375,910),(1375,810),(1400,810)],target='A3.5',role='I',flow='task_results')
a3.text(900,938,235,57,'Результати й\nдіагностика задач',19)
a3.arrow([(1610,805),(1770,805)],source='A3.5',flow='canonical',boundary=('O','O1'))
a3.text(1615,710,155,82,'Канонічні моделі,\nрезультати\nта метрики',19,inline=True)

def audit():
    results=[]
    for p in PAGES:
        assert len(p.boxes)==({'A-0':1,'A0':5,'A2':4,'A3':5}[p.node])
        for node,ports in p.ports.items():
            assert all(ports[k] for k in 'ICOM'), (p.node,node,ports)
        for n,(x,y,w,h,_) in p.boxes.items():
            for nn,(xx,yy,ww,hh,_) in p.boxes.items():
                if n>=nn: continue
                assert not (x<xx+ww and x+w>xx and y<yy+hh and y+h>yy),(p.node,'overlapping functions',n,nn)
        for r in p.routes:
            pts=r['points']
            assert all(math.isfinite(c) for xy in pts for c in xy)
            for (x,y),(xx,yy) in zip(pts,pts[1:]):
                assert x==xx or y==yy,(p.node,r['id'],'nonorthogonal')
                for n,(bx,by,bw,bh,id) in p.boxes.items():
                    hit=(bx<x<bx+bw and max(min(y,yy),by)<min(max(y,yy),by+bh)) if x==xx else (by<y<by+bh and max(min(x,xx),bx)<min(max(x,xx),bx+bw))
                    assert not hit,(p.node,r['id'],'crosses',n)
            if r['source']:
                bx,by,bw,bh,_=p.boxes[r['source']]
                assert pts[0][0]==bx+bw and by<=pts[0][1]<=by+bh
                assert pts[1][0]>pts[0][0],(p.node,r['id'],'output direction')
            if r['target']:
                bx,by,bw,bh,_=p.boxes[r['target']];x,y=pts[-1];px,py=pts[-2]
                ok={'I':x==bx and by<=y<=by+bh and px<x and py==y,
                    'C':y==by and bx<=x<=bx+bw and py<y and px==x,
                    'M':y==by+bh and bx<=x<=bx+bw and py>y and px==x}
                assert ok[r['role']],(p.node,r['id'],'wrong ICOM side')
        results.append({'page':p.node,'functions':len(p.boxes),'ports':{n:{k:sorted(v) for k,v in d.items()} for n,d in p.ports.items()},'boundary':p.boundary})
    for parent,node,child in [(ctx,'A0',a0),(a0,'A2',a2),(a0,'A3',a3)]:
        actual={k:{flow for kind,flow in child.boundary.values() if kind==k} for k in 'ICOM'}
        assert parent.ports[node]==actual,('unbalanced',node,parent.ports[node],actual)
    return results


def preview(page, xmlpage):
    """Export the saved XML's plain rectangle, text, and orthogonal line subset."""
    cells=xmlpage.findall('.//mxCell'); byid={c.get('id'):c for c in cells}
    im=Image.new('RGB',(W*2,H*2),'white');d=ImageDraw.Draw(im)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>']
    def geom(c):
        g=c.find('mxGeometry');x,y,w,h=[float(g.get(k,0)) for k in ('x','y','width','height')]
        parent=byid.get(c.get('parent'))
        if parent is not None and parent.get('vertex')=='1':
            px,py,_,_=geom(parent);x+=px;y+=py
        return x,y,w,h
    def style(c): return dict(t.split('=',1) for t in c.get('style','').split(';') if '=' in t)
    # Edges first, with small white crossing clearance. Junction dots added last.
    for c in cells:
        if c.get('edge')!='1':continue
        s=style(c);g=c.find('mxGeometry')
        a=g.find("mxPoint[@as='sourcePoint']");b=g.find("mxPoint[@as='targetPoint']")
        pts=[(float(a.get('x')),float(a.get('y')))]+[(float(v.get('x')),float(v.get('y'))) for v in g.findall('./Array/mxPoint')]+[(float(b.get('x')),float(b.get('y')))]
        for color,width in [('white',5),('#000000',1.2)]:
            d.line([(x*2,y*2) for x,y in pts],fill=color,width=int(width*2))
            svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{color}" stroke-width="{width}"/>')
        if s.get('endArrow')!='none':
            (x,y),(xx,yy)=pts[-2:];a=math.atan2(yy-y,xx-x)
            tri=[(xx,yy),(xx-11*math.cos(a)+4*math.sin(a),yy-11*math.sin(a)-4*math.cos(a)),(xx-11*math.cos(a)-4*math.sin(a),yy-11*math.sin(a)+4*math.cos(a))]
            d.polygon([(x*2,y*2) for x,y in tri],fill='#000000')
            svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in tri)}" fill="#000000"/>')
    for c in cells:
        if c.get('vertex')!='1':continue
        s=style(c);x,y,w,h=geom(c)
        if s.get('fillColor')=='#FFFFFF':
            border=s.get('strokeColor')!='none'
            d.rectangle((x*2,y*2,(x+w)*2,(y+h)*2),fill='white',outline='#000000' if border else None,width=2)
            svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="{"#000000" if border else "none"}" stroke-width="1.2"/>')
        if 'ellipse;' in c.get('style',''):
            d.ellipse((x*2,y*2,(x+w)*2,(y+h)*2),fill='#000000')
            svg.append(f'<circle cx="{x+w/2}" cy="{y+h/2}" r="2" fill="#000000"/>')
        text=c.get('value','')
        if not text:continue
        size=int(s['fontSize']);bold=s.get('fontStyle')=='1'
        f=ImageFont.truetype('C:/Windows/Fonts/'+('arialbd.ttf' if bold else 'arial.ttf'),size*2)
        lines=text.split('\n');step=size*1.18
        assert len(lines)*step<=h+1,(page.node,text,'height')
        for i,t in enumerate(lines):
            assert d.textlength(t,font=f)/2<=w,(page.node,t,'width',w,d.textlength(t,font=f)/2)
            align=s.get('align','center')
            xx=x+w if align=='right' else x if align=='left' else x+w/2
            yy=y+h/2+(i-(len(lines)-1)/2)*step
            tw=d.textlength(t,font=f)/2
            left=xx-tw if align=='right' else xx if align=='left' else xx-tw/2
            right=left+tw;top=yy-size*.47;bottom=yy+size*.47
            for r in page.routes:
                for (ax,ay),(bx,by) in zip(r['points'],r['points'][1:]):
                    hit=(left<ax<right and max(min(ay,by),top)<min(max(ay,by),bottom)) if ax==bx else (top<ay<bottom and max(min(ax,bx),left)<min(max(ax,bx),right))
                    assert not hit or c.get('inlineLabel')=='1',(page.node,'label/line collision',t,r['id'])
            d.text((xx*2,yy*2),t,font=f,fill='#000000',anchor={'left':'lm','right':'rm','center':'mm'}[align])
            anchor={"left":"start","right":"end","center":"middle"}[align]
            svg.append(f'<text x="{xx}" y="{yy}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}" dominant-baseline="central" fill="#000000">{escape(t)}</text>')
    svg.append('</svg>')
    (PREVIEW/f'{page.slug}.svg').write_text('\n'.join(svg),encoding='utf-8')
    im.save(PREVIEW/f'{page.slug}.png',dpi=(300,300))


if __name__=='__main__':
    report=audit()
    ET.indent(DOC)
    path=OUT/'fmcg_idef0.drawio'
    ET.ElementTree(DOC).write(path,encoding='utf-8',xml_declaration=True)
    saved=ET.parse(path);ids=[c.get('id') for c in saved.findall('.//mxCell')]
    assert len(ids)==len(set(ids))
    for c in saved.findall('.//mxCell'):
        for ref in ('parent','source','target'):
            assert c.get(ref) is None or c.get(ref) in ids
    for g in saved.findall('.//mxGeometry')+saved.findall('.//mxPoint'):
        for key in ('x','y','width','height'):
            if key in g.attrib: assert math.isfinite(float(g.get(key)))
    PREVIEW.mkdir(exist_ok=True)
    for page,xml in zip(PAGES,saved.findall('./diagram')):preview(page,xml)
    (OUT/'fmcg_idef0_validation.json').write_text(json.dumps({'xml':'PASS','unique_ids':len(ids),'page_count':4,'function_count':15,'icom_sides':'PASS','balance':'PASS','function_overlaps':0,'unrelated_box_crossings':0,'unmasked_label_line_collisions':0,'text_fit':'PASS','gui_import':'NOT_TESTED','preview_method':'XML primitive exporter','pages':report},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'PASS: 4 pages, 15 functions, {len(ids)} unique cells; ICOM directions; 3 parent/child balances; orthogonal routes; no box crossings; text fit; XML-based SVG/PNG previews.')
