"""Build the documentation-only, editable Gane–Sarson DFD and audit its graph.

No application modules, data pipelines or runtime services are invoked.
"""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET
from PIL import ImageFont

BASE = Path(__file__).resolve().parent
DOC = ET.Element('mxfile', host='app.diagrams.net')
PAGES = []
W, H = 2100, 1400
FONT = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 23)
STORES = {
 'D1': 'Початкові та\nінтегровані дані',
 'D2': 'Операційні\nFMCG-дані',
 'D3': 'Аналітичне\nсховище',
 'D4': 'Набори для\nаналітичних задач',
 'D5': 'Канонічні ML/\nаналітичні артефакти\nта результати',
 'D6': 'Метадані експериментів,\nзапусків і версій\nартефактів',
 'D7': 'Звіти якості\nнаборів даних',
 'D8': 'Черга replay-подій\nKafka',
}
EXTERNAL_IN = 'Зовнішні FMCG-дані\nта довідкові набори'
REQUEST = 'Параметри прогнозування\nта аналітичних запитів'
RESPONSE = 'Прогнози, ризики, KPI\nта аналітичні результати'
DATASETS = ['forecast_data', 'stockout_data', 'segment_data', 'anomaly_data', 'basket_data', 'promotion_data']
ML_INPUTS = DATASETS + ['stockout_episodes']
RESULTS = ['forecast_result', 'risk_result', 'survival_result', 'segment_result', 'anomaly_result', 'basket_result', 'promotion_result']


class Page:
    def __init__(self, slug, name, title):
        self.slug, self.nodes, self.flows, self.labels = slug, {}, [], []
        self.i = 0
        d = ET.SubElement(DOC, 'diagram', id=slug, name=name)
        m = ET.SubElement(d, 'mxGraphModel', page='1', pageWidth=str(W), pageHeight=str(H), pageScale='1', grid='1', gridSize='10', background='#FFFFFF')
        self.root = ET.SubElement(m, 'root')
        ET.SubElement(self.root, 'mxCell', id=slug+'-0')
        self.layer = slug+'-1'
        ET.SubElement(self.root, 'mxCell', id=self.layer, parent=slug+'-0')
        self.text(40, 35, 2020, 55, title, size=32, bold=True)
        self.text(40, 1360, 2020, 35, 'Gane–Sarson' if slug == 'dfd_context' else 'Gane–Sarson · Повторення позначення D означає те саме логічне сховище.', size=21)
        PAGES.append(self)

    def cell(self, value, box, style, parent=None, **attr):
        self.i += 1
        cid = self.slug + '-c' + str(self.i)
        c = ET.SubElement(self.root, 'mxCell', id=cid, value=value, style=style, vertex='1', parent=parent or self.layer, **attr)
        x,y,w,h = box
        ET.SubElement(c,'mxGeometry', x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        return cid

    def text(self,x,y,w,h,value,size=23,bold=False,parent=None):
        font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf', size)
        assert max(font.getlength(line) for line in value.split('\n')) < w - 4, (self.slug, value, w)
        assert len(value.split('\n')) * size * 1.17 <= h, (value,h)
        if parent is None: self.labels.append((value,(x,y,w,h)))
        return self.cell(value,(x,y,w,h),f'text;html=0;whiteSpace=wrap;strokeColor=none;fillColor=none;fontColor=#111111;fontFamily=Arial;fontSize={size};fontStyle={int(bold)};spacing=0;align=center;verticalAlign=middle;',parent)

    def line(self,x,y,w,h,parent):
        self.cell('',(x,y,max(w,1),max(h,1)),'shape=line;strokeColor=#222222;strokeWidth=1.5;'+('direction=south;' if w==0 else ''),parent)

    def node(self,key,kind,box,title=None,logical=None):
        x,y,w,h=box
        logical=logical or key
        style='html=0;fillColor=#FFFFFF;strokeColor=#222222;strokeWidth=1.5;container=1;collapsible=0;'
        if kind=='process': style+='rounded=1;arcSize=14;'
        elif kind=='store': style+='strokeColor=none;'
        cid=self.cell('',box,style,dfdType=kind,logicalId=logical)
        if kind=='process':
            self.text(8,5,w-16,32,logical,size=23,parent=cid)
            self.line(0,42,w,0,cid)
            self.text(10,49,w-20,h-55,title,parent=cid)
        elif kind=='store':
            self.line(0,0,w,0,cid); self.line(0,h,w,0,cid)
            self.line(0,0,0,h,cid); self.line(48,0,0,h,cid)
            self.text(2,0,43,h,logical,size=22,parent=cid)
            self.text(56,0,w-64,h,title or STORES[logical],parent=cid)
        else:
            self.text(10,5,w-20,h-10,title,parent=cid)
        self.nodes[key]={'id':cid,'kind':kind,'logical':logical,'box':box,'title':title}

    def flow(self,source,target,label,points,lb,sem,optional=False):
        self.i+=1
        sid,tid=self.nodes[source],self.nodes[target]
        style='edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;strokeColor=#222222;strokeWidth=1.5;endArrow=block;endFill=1;'
        for n,p,prefix in [(sid,points[0],'exit'),(tid,points[-1],'entry')]:
            x,y,w,h=n['box']
            style+=f'{prefix}X={(p[0]-x)/w};{prefix}Y={(p[1]-y)/h};{prefix}Perimeter=0;'
        if optional: style+='dashed=1;dashPattern=7 4;'
        c=ET.SubElement(self.root,'mxCell',id=f'{self.slug}-e{self.i}',value='',style=style,edge='1',parent=self.layer,source=sid['id'],target=tid['id'],flowLabel=label,semanticAtoms='|'.join(sem))
        g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
        for p,role in [(points[0],'sourcePoint'),(points[-1],'targetPoint')]:
            ET.SubElement(g,'mxPoint',x=str(p[0]),y=str(p[1]),attrib={'as':role})
        if len(points)>2:
            a=ET.SubElement(g,'Array',attrib={'as':'points'})
            for x,y in points[1:-1]: ET.SubElement(a,'mxPoint',x=str(x),y=str(y))
        self.text(*lb,label)
        self.flows.append({'source':source,'target':target,'label':label,'points':points,'atoms':sem,'label_box':lb})


def context():
    p=Page('dfd_context','Context','Контекстна DFD системи FMCG Sales Intelligence')
    p.node('E1','entity',(70,580,350,150),'E1\nЗовнішні джерела\nFMCG / retail-даних')
    p.node('0','process',(780,540,490,225),'Обробляти FMCG-дані\nта надавати\nаналітичні результати')
    p.node('E2','entity',(1680,580,350,150),'E2\nБізнес-користувач /\nаналітик')
    p.flow('E1','0',EXTERNAL_IN,[(420,650),(780,650)],(435,565,330,65),['source_data'])
    p.flow('E2','0',REQUEST,[(1680,615),(1500,615),(1500,460),(1100,460),(1100,540)],(1225,375,410,65),['request'])
    p.flow('0','E2',RESPONSE,[(1270,690),(1680,690)],(1290,720,370,65),['response'])


def level1():
    p=Page('dfd_level_1','Level 1','DFD рівня 1 — основні потоки даних')
    p.node('E1','entity',(40,220,290,125),'E1\nЗовнішні джерела\nFMCG / retail-даних')
    p.node('1.0','process',(460,210,310,140),'Інтегрувати та\nперевіряти FMCG-дані')
    p.node('D2','store',(930,235,300,100))
    p.node('2.0','process',(1430,210,310,140),'Формувати аналітичні\nнабори даних')
    p.node('D1','store',(460,530,340,100))
    p.node('D8','store',(40,535,355,110))
    p.node('D3','store',(1430,530,310,100))
    p.node('D7','store',(1810,530,250,100))
    p.node('D4','store',(1430,810,320,100))
    p.node('3.0','process',(930,790,310,140),'Виконувати ML та\nаналітичну обробку')
    p.node('D5','store',(460,810,330,100))
    p.node('4.0','process',(460,1150,330,140),'Реєструвати аналітичні\nартефакти та метадані')
    p.node('D6','store',(40,1170,340,100))
    p.node('5.0','process',(1430,1150,320,140),'Надавати прогнози та\nаналітичні результати')
    p.node('E2','entity',(1830,1150,240,140),'E2\nБізнес-користувач /\nаналітик')
    p.flow('E1','1.0',EXTERNAL_IN,[(330,275),(460,275)],(270,135,300,65),['source_data'])
    p.flow('1.0','D2','Операційні\nзаписи',[(770,285),(930,285)],(775,300,150,65),['operational_write'])
    p.flow('D2','2.0','Факти та\nдовідники',[(1230,285),(1430,285)],(1240,195,180,65),['operational'])
    p.flow('1.0','D1','Збережені початкові\nта інтегровані дані',[(700,350),(700,530)],(710,395,305,65),['source_files_write'])
    p.flow('D1','1.0','Початкові\nнабори та\nпараметри\nкалібрування',[(520,530),(520,350)],(525,375,170,115),['source_files_read'])
    p.flow('D2','1.0','Продажі для replay\n(опціонально)',[(1080,235),(1080,125),(710,125),(710,210)],(775,145,270,65),['replay_sales'],True)
    p.flow('1.0','D8','Опубліковані\nreplay-події',[(460,325),(420,325),(420,465),(320,465),(320,535)],(75,390,315,65),['replay_write'],True)
    p.flow('D8','1.0','Потік FMCG-подій\n(опціонально; Kafka)',[(350,645),(350,765),(440,765),(440,345),(460,345)],(40,675,300,65),['replay_read'],True)
    p.flow('2.0','D3','Аналітичні\nдані та\nвітрини',[(1510,350),(1510,530)],(1360,385,145,95),['raw','transformed','marts'])
    p.flow('D3','2.0','Аналітичні\nдані та\nвітрини',[(1630,530),(1630,350)],(1640,385,135,95),['raw','transformed','marts'])
    p.flow('2.0','D4','Ознаки, цілі\nта набори задач',[(1430,330),(1340,330),(1340,860),(1430,860)],(1135,600,195,65),DATASETS)
    p.flow('D4','2.0','Сформовані набори\nдля перевірки',[(1750,850),(1780,850),(1780,270),(1740,270)],(1800,735,275,65),DATASETS)
    p.flow('2.0','D7','Результати\nперевірок якості',[(1740,320),(1935,320),(1935,530)],(1820,230,270,65),['quality'])
    p.flow('D4','3.0','Підготовлені набори для\nML та аналітичних задач',[(1430,890),(1240,890)],(1160,935,355,65),ML_INPUTS)
    p.flow('3.0','D5','ML/аналітичні артефакти,\nметрики та результати',[(930,860),(790,860)],(745,700,410,65),RESULTS)
    p.flow('D5','4.0','Метрики,\nманіфести та\nаналітичні\nартефакти',[(620,910),(620,1150)],(650,940,180,115),['tracking_input'])
    p.flow('D6','4.0','Наявні записи\nекспериментів і запусків',[(380,1200),(460,1200)],(140,1080,300,65),['tracking_existing'])
    p.flow('4.0','D6','Ідентифікатори запусків\nі версії артефактів',[(460,1250),(380,1250)],(95,1275,330,55),['tracking_metadata'])
    p.flow('D5','5.0','Підтримувані ML-артефакти\nта аналітичні результати',[(790,890),(840,890),(840,1050),(1510,1050),(1510,1150)],(985,1060,405,65),['serving_artifacts'])
    p.flow('D3','5.0','Аналітичні вітрини\nдля KPI та фільтрів',[(1610,630),(1610,720),(1770,720),(1770,1080),(1660,1080),(1660,1150)],(1800,965,290,65),['bi_marts'])
    p.flow('E2','5.0',REQUEST,[(1830,1190),(1750,1190)],(1780,1070,310,65),['request'])
    p.flow('5.0','E2',RESPONSE,[(1750,1250),(1830,1250)],(1720,1295,375,55),['response'])
    p.text(55,945,345,105,'Пунктир — опціональний replay.',size=22)


def data_level():
    p=Page('dfd_level_2_data','Level 2 — Data Preparation','DFD рівня 2 — формування аналітичних наборів (2.0)')
    # Persisted stages are deliberately repeated as D3, not invented stores.
    for key,logical,box in [
        ('D2','D2',(45,210,325,100)),('raw','D3',(1040,210,320,100)),
        ('trans','D3',(1040,440,320,100)),
        ('marts','D3',(1040,670,320,100)),
        ('marts2','D3',(45,900,325,100)),('D4','D4',(1040,900,320,100)),
        ('qualityin','D4',(45,1130,325,100)),('D7','D7',(1040,1130,320,100))]:
        p.node(key,'store',box,logical=logical)
    titles=['Отримувати операційні\nфакти та довідники','Узгоджувати аналітичну\nструктуру даних','Формувати\nаналітичні вітрини','Будувати ознаки, цілі\nта набори задач','Перевіряти якість\nсформованих наборів']
    rows=[(210,'D2','raw','Факти та\nдовідники','Репліка\nопераційних даних',['operational'],['raw']),
          (440,'raw','trans','Репліка\nопераційних даних','Узгоджені факти\nта виміри',['raw'],['transformed']),
          (670,'trans','marts','Узгоджені дані\nта репліка умов','Аналітичні\nвітрини',['transformed','raw'],['marts']),
          (900,'marts2','D4','Факти, виміри, вітрини,\nціни та промоумови','Ознаки, цілі\nта набори задач',['raw','transformed','marts'],DATASETS),
          (1130,'qualityin','D7','Сформовані набори\nдля перевірки','Результати\nперевірок якості',DATASETS,['quality'])]
    for i,(y,a,b,il,ol,ia,oa) in enumerate(rows,1):
        key=f'2.{i}';p.node(key,'process',(620,y-15,330,140),titles[i-1])
        if i in (2,3):
            p.flow(a,key,il,[(1100,y-130),(1100,y-95),(540,y-95),(540,y+50),(620,y+50)],(235,y-10,295,65),ia)
        else:
            p.flow(a,key,il,[(370,y+50),(620,y+50)],(350,y-70 if i==5 else y-90,270,55 if i==5 else 65),ia)
        p.flow(key,b,ol,[(950,y+50),(1040,y+50)],(940,y-70 if i==5 else y-90,300,55 if i==5 else 65),oa)
    p.text(1430,220,620,150,'D3 містить репліковані дані,\nузгоджені аналітичні структури\nта вітрини.',size=24)


def ml_level():
    p=Page('dfd_level_2_ml','Level 2 — ML & Analytics','DFD рівня 2 — ML та аналітична обробка (3.0)')
    tasks=[
      ('Прогнозувати\nобсяг продажів','Історичні ознаки\nта цілі продажів','Модель, прогноз\nпродажів і метрики',['forecast_data'],'forecast_result'),
      ('Оцінювати\nризик дефіциту','Запаси, ознаки\nта епізоди дефіциту','Модель, ризики\nдефіциту і метрики',['stockout_data','stockout_episodes'],'risk_result'),
      ('Оцінювати час до\nдефіциту (офлайн)','Запаси, епізоди\nта цензурування','Модель, оцінки часу\nдо дефіциту, метрики',['stockout_data','stockout_episodes'],'survival_result'),
      ('Групувати\nмагазини','Агреговані ознаки\nмагазинів','Модель, дослідницькі\nкластери і метрики',['segment_data'],'segment_result'),
      ('Виявляти\nаномальні спостереження','Спостереження\nта історичні бази','Модель, кандидати\nаномалій і метрики',['anomaly_data'],'anomaly_result'),
      ('Виявляти асоціації\nтоварів у кошиках','Позиції замовлень\nі склад кошиків','Асоціативні правила\nта їхні метрики',['basket_data'],'basket_result'),
      ('Порівнювати показники\nпромоперіодів','Щоденні промодані\nта підсумки кампаній','Описові порівняння\nпромо та метрики',['promotion_data'],'promotion_result'),
    ]
    # Seven independent branches; common stores repeat to keep routing legible.
    for i,(title,il,ol,ia,oa) in enumerate(tasks,1):
        y=190+(i-1)*155
        a=f'in{i}';b=f'out{i}';n=f'3.{i}'
        p.node(a,'store',(45,y+15,325,90),logical='D4')
        p.node(n,'process',(800,y,380,125),title)
        p.node(b,'store',(1650,y+15,380,90),logical='D5')
        p.flow(a,n,il,[(370,y+62),(800,y+62)],(400,y-10,370,65),ia)
        p.flow(n,b,ol,[(1180,y+62),(1650,y+62)],(1210,y-10,410,65),[oa])
    p.text(45,1270,1985,45,'Кластери — дослідницькі; промопорівняння — не причинний ефект.',size=22)


def boundary(page, process=None, external=False):
    atoms=set()
    for f in page.flows:
        a,b=page.nodes[f['source']],page.nodes[f['target']]
        if external:
            if a['kind']=='entity': atoms.update(('in',a['logical'],s) for s in f['atoms'])
            if b['kind']=='entity': atoms.update(('out',b['logical'],s) for s in f['atoms'])
        elif process:
            if a['logical']==process: atoms.update(('out',b['logical'],s) for s in f['atoms'])
            if b['logical']==process: atoms.update(('in',a['logical'],s) for s in f['atoms'])
        else:
            if a['kind']=='store': atoms.update(('in',a['logical'],s) for s in f['atoms'])
            if b['kind']=='store': atoms.update(('out',b['logical'],s) for s in f['atoms'])
    return atoms


def audit():
    checks=[]
    for p in PAGES:
        def overlap(a,b):
            x,y,w,h=a; u,v,r,s=b
            return max(x,u)<min(x+w,u+r) and max(y,v)<min(y+h,v+s)
        nodes=list(p.nodes.items())
        for i,(key,node) in enumerate(nodes):
            for other,on in nodes[i+1:]:
                assert not overlap(node['box'],on['box']),('nodes overlap',key,other)
        for i,(label,box) in enumerate(p.labels):
            x,y,w,h=box
            assert 0<=x and 0<=y and x+w<=W and y+h<=H
            for other,ob in p.labels[i+1:]:
                assert not overlap(box,ob),('labels overlap',p.slug,label,other)
            for key,n in p.nodes.items():
                assert not overlap(box,n['box']),('label overlaps node',p.slug,label,key)
            for f in p.flows:
                for (x1,y1),(x2,y2) in zip(f['points'],f['points'][1:]):
                    hit=(x1==x2 and x<x1<x+w and max(min(y1,y2),y)<min(max(y1,y2),y+h)) or (y1==y2 and y<y1<y+h and max(min(x1,x2),x)<min(max(x1,x2),x+w))
                    assert not hit,('flow through label',p.slug,label,f['label'])
        for f in p.flows:
            a,b=p.nodes[f['source']],p.nodes[f['target']]
            assert 'process' in (a['kind'],b['kind']), ('forbidden direct connection',f)
            assert f['label'] and f['atoms']
            for (x1,y1),(x2,y2) in zip(f['points'],f['points'][1:]):
                assert x1==x2 or y1==y2,('nonorthogonal',f)
                for key,n in p.nodes.items():
                    if key in (f['source'],f['target']): continue
                    x,y,w,h=n['box']
                    hit=(x1==x2 and x<x1<x+w and max(min(y1,y2),y)<min(max(y1,y2),y+h)) or (y1==y2 and y<y1<y+h and max(min(x1,x2),x)<min(max(x1,x2),x+w))
                    assert not hit,('flow through node',p.slug,f['label'],key)
        for key,n in p.nodes.items():
            if n['kind']=='process':
                assert any(f['target']==key for f in p.flows),('miracle',key)
                assert any(f['source']==key for f in p.flows),('black hole',key)
        checks.append({'page':p.slug,'processes':sum(n['kind']=='process' for n in p.nodes.values()),'flows':len(p.flows)})
    balances=[('Context → Level 1',boundary(PAGES[0],external=True),boundary(PAGES[1],external=True)),
              ('2.0 → Level 2',boundary(PAGES[1],'2.0'),boundary(PAGES[2])),
              ('3.0 → Level 2',boundary(PAGES[1],'3.0'),boundary(PAGES[3]))]
    for label,a,b in balances: assert a==b,(label,'missing',a-b,'new',b-a)
    out=BASE/'fmcg_dfd.drawio'
    ET.indent(DOC)
    ET.ElementTree(DOC).write(out,encoding='utf-8',xml_declaration=True)
    tree=ET.parse(out)
    assert len(tree.findall('diagram'))==4
    assert sum(n['kind']=='process' for n in PAGES[0].nodes.values())==1
    assert all(n['kind']!='store' for n in PAGES[0].nodes.values())
    cells=tree.findall('.//mxCell');ids=[c.get('id') for c in cells]
    assert len(ids)==len(set(ids))
    for c in cells:
        for key in ['parent','source','target']:
            if c.get(key): assert c.get(key) in ids
    for g in tree.findall('.//mxGeometry')+tree.findall('.//mxPoint'):
        for key in ['x','y','width','height']:
            if g.get(key): assert math.isfinite(float(g.get(key)))
    report={'xml':'PASS','unique_cells':len(cells),'pages':checks,'forbidden_direct_flows':0,'black_holes':0,'zero_input_processes':0,'unlabelled_flows':0,'orthogonal_routes':'PASS','routes_through_unrelated_nodes':0,'label_collisions':0,'text_fit':'PASS','balancing':{n:{'status':'PASS','atoms':[list(v) for v in sorted(a)]} for n,a,b in balances},'miracle_gray_hole_review':'See source-based process audit in fmcg_dfd_audit.md'}
    (BASE/'fmcg_dfd_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'xml':'PASS','cells':len(cells),'pages':checks},ensure_ascii=False))


if __name__=='__main__':
    context();level1();data_level();ml_level();audit()
