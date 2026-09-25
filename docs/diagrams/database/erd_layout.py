"""Native editable ER diagrams with explicit min/max cardinality and routed edges."""
from pathlib import Path
import heapq
import os
import random
import xml.etree.ElementTree as ET
from PIL import ImageFont

BASE=Path(__file__).resolve().parent


def intersects(a,b):
    x,y,w,h=a;u,v,r,s=b
    return max(x,u)<min(x+w,u+r) and max(y,v)<min(y+h,v+s)


def line_hits(a,b,box):
    x,y,w,h=box;x1,y1=a;x2,y2=b
    return ((x1==x2 and x<x1<x+w and max(min(y1,y2),y)<min(max(y1,y2),y+h)) or
            (y1==y2 and y<y1<y+h and max(min(x1,x2),x)<min(max(x1,x2),x+w)))


class Diagram:
    def __init__(self,slug,title,w,h,physical):
        self.slug,self.w,self.h,self.physical=slug,w,h,physical
        self.doc=ET.Element('mxfile',host='app.diagrams.net',type='device')
        page=ET.SubElement(self.doc,'diagram',id=slug,name='Physical ERD' if physical else 'Logical ERD')
        model=ET.SubElement(page,'mxGraphModel',page='1',pageWidth=str(w),pageHeight=str(h),pageScale='1',grid='1',gridSize='10',background='#FFFFFF')
        self.root=ET.SubElement(model,'root');ET.SubElement(self.root,'mxCell',id='0');ET.SubElement(self.root,'mxCell',id='1',parent='0')
        self.i=1;self.nodes={};self.links=[];self.routes=[];self.labels=[];self.obstacles=[]
        self.text(title,50,22,w-100,48,32,True)

    def cell(self,value,box,style,parent='1',**attrs):
        self.i+=1;cid=f'v{self.i}'
        c=ET.SubElement(self.root,'mxCell',id=cid,parent=parent,value=value,style=style,vertex='1',**attrs)
        x,y,w,h=box;ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        return cid

    def text(self,value,x,y,w,h,size=22,bold=False,parent='1',align='left',color='#222222'):
        font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',size)
        assert max(font.getlength(t) for t in value.split('\n'))<=w-4,(value,w,size)
        assert len(value.split('\n'))*size*1.16<=h,(value,h,size)
        cid=self.cell(value,(x,y,w,h),f'text;html=0;whiteSpace=wrap;strokeColor=none;fillColor=none;spacing=0;fontFamily=Arial;fontSize={size};fontStyle={int(bold)};fontColor={color};align={align};verticalAlign=middle;',parent)
        if parent=='1':self.labels.append((value,(x,y,w,h)))
        return cid

    def box(self,name,x,y,w,rows,checks=(),physical=None):
        physical=self.physical if physical is None else physical
        rh=27 if physical else 30;head=42; h=head+len(rows)*rh+12+len(checks)*26
        cid=self.cell('',(x,y,w,h),'rounded=0;html=0;fillColor=#FFFFFF;strokeColor=#333333;strokeWidth=1.4;container=1;collapsible=0;',entity=name)
        self.cell('',(0,0,w,head),'rounded=0;fillColor=#EEEEEE;strokeColor=#333333;strokeWidth=1.4;',cid)
        self.text(name,12,3,w-24,35,25,True,cid,align='center')
        column_rows={}
        for i,row in enumerate(rows):
            ry=head+i*rh
            if physical:
                marker,column,typ,null=row
                self.text(marker,8,ry,80,rh,17,False,cid)
                self.text(column,94,ry,340,rh,22,False,cid)
                self.text(typ,442,ry,160,rh,20,False,cid)
                self.text(null,610,ry,34,rh,18,False,cid)
                column_rows[column]=y+ry+rh/2
            else:self.text(row,14,ry,w-28,rh,23,False,cid)
        for i,chk in enumerate(checks):self.text(chk,12,head+len(rows)*rh+6+i*26,w-24,26,20,False,cid,color='#444444')
        self.nodes[name]={'id':cid,'box':(x,y,w,h),'rows':column_rows,'physical':physical}
        return h

    def link(self,a,b,ca,cb,field=None,parent_field=None,role=''):
        self.links.append({'a':a,'b':b,'ca':ca,'cb':cb,'field':field,'parent_field':parent_field,'role':role})

    def candidates(self,name,card,column=None):
        n=self.nodes[name];x,y,w,h=n['box']
        if column:py=n['rows'][column]
        else:py=y+42+(h-54)*({'1':.1,'0..1':.5,'0..N':.9}[card])
        return [v for v in [((x,py),(x-28,py),(-1,0)),((x+w,py),(x+w+28,py),(1,0))] if 80<v[0][0]<self.w-80 and (not self.physical or name not in ('categories','orders','promotions') or card=='0..N' or (card=='1' and v[2][0]==1) or (card=='0..1' and v[2][0]==-1))]

    def label_box(self,point,side):
        x,y=point;return (x-72 if side[0]<0 else x+8,y-(24 if self.physical else 27),64,20 if self.physical else 23)

    def route_all(self):
        # Include every candidate endpoint label as a routing obstacle before drawing.
        endpoint_labels=[];ends=[]
        for f in self.links:
            ac=self.candidates(f['a'],f['ca'],f['field']);bc=self.candidates(f['b'],f['cb'],f['parent_field'])
            ends.append((ac,bc))
            for point,stub,side in ac+bc:endpoint_labels.append(self.label_box(point,side))
        obstacles=[n['box'] for n in self.nodes.values()]+[b for _,b in self.labels]+endpoint_labels
        xs=set(range(18,self.w-10,22));ys=set(range(100,self.h-80,22))
        for x,y,w,h in obstacles:
            xs.update([x-8,x+w+8]);ys.update([y-8,y+h+8])
        for ac,bc in ends:
            for point,stub,side in ac+bc:xs.add(stub[0]);ys.add(stub[1])
        xs=sorted(x for x in xs if 12<x<self.w-12);ys=sorted(y for y in ys if 100<y<self.h-95)
        xi={x:i for i,x in enumerate(xs)};yi={y:i for i,y in enumerate(ys)}
        free={};used={};directions={};all_paths={}
        def allowed(ix,iy):
            key=(ix,iy)
            if key not in free:
                x,y=xs[ix],ys[iy]
                free[key]=not any(a-3<x<a+w+3 and b-3<y<b+h+3 for a,b,w,h in obstacles)
            return free[key]
        def metric(f):
            a=self.nodes[f['a']]['box'];b=self.nodes[f['b']]['box']
            return abs(a[0]-b[0])+abs(a[1]-b[1])
        mode=os.getenv('ERD_ROUTE_ORDER','4' if self.physical else 'short')
        order=sorted(range(len(self.links)),key=lambda i:metric(self.links[i]),reverse=mode=='long')
        if mode not in ('short','long'):random.Random(int(mode)).shuffle(order)
        for no in order:
            ac,bc=ends[no]
            starts={(xi[s[0]],yi[s[1]]):j for j,(_,s,_) in enumerate(ac)}
            goals={(xi[s[0]],yi[s[1]]):j for j,(_,s,_) in enumerate(bc)}
            q=[];dist={};prev={};origin={}
            def heuristic(ix,iy):return min(abs(xs[ix]-xs[gx])+abs(ys[iy]-ys[gy]) for gx,gy in goals)
            for (ix,iy),j in starts.items():
                state=(ix,iy,0);dist[state]=0;origin[state]=j
                heapq.heappush(q,(heuristic(ix,iy),0,state))
            final=None
            while q:
                _,cost,state=heapq.heappop(q)
                if cost!=dist.get(state):continue
                ix,iy,d=state
                if (ix,iy) in goals:final=state;break
                for dx,dy,nd in [(1,0,0),(-1,0,0),(0,1,1),(0,-1,1)]:
                    nx,ny=ix+dx,iy+dy
                    if not (0<=nx<len(xs) and 0<=ny<len(ys)) or not allowed(nx,ny):continue
                    a=(ix,iy);b=(nx,ny);ek=tuple(sorted([a,b]))
                    length=abs(xs[ix]-xs[nx])+abs(ys[iy]-ys[ny])
                    penalty=length*(1+8*used.get(ek,0))+(40 if nd!=d else 0)
                    if directions.get(b,set())-{nd}:penalty+=12000
                    ncost=cost+penalty;nstate=(nx,ny,nd)
                    if ncost<dist.get(nstate,float('inf')):
                        dist[nstate]=ncost;prev[nstate]=state;origin[nstate]=origin[state]
                        heapq.heappush(q,(ncost+heuristic(nx,ny),ncost,nstate))
            assert final is not None,('no route',self.links[no],[(xs[ix],ys[iy],allowed(ix,iy),[o for o in obstacles if o[0]-3<xs[ix]<o[0]+o[2]+3 and o[1]-3<ys[iy]<o[1]+o[3]+3]) for ix,iy in list(starts)+list(goals)])
            path=[];state=final
            while True:
                path.append((state[0],state[1]))
                if state not in prev:break
                state=prev[state]
            path.reverse()
            for a,b in zip(path,path[1:]):
                ek=tuple(sorted([a,b]));used[ek]=used.get(ek,0)+1
                nd=0 if a[1]==b[1] else 1
                directions.setdefault(a,set()).add(nd);directions.setdefault(b,set()).add(nd)
            first=ac[origin[final]];last=bc[goals[(final[0],final[1])]]
            points=[first[0]]+[(xs[ix],ys[iy]) for ix,iy in path]+[last[0]]
            compact=[points[0]]
            for i in range(1,len(points)-1):
                a=compact[-1];b=points[i];c=points[i+1]
                if (a[0]==b[0]==c[0]) or (a[1]==b[1]==c[1]):continue
                compact.append(b)
            compact.append(points[-1]);all_paths[no]=(compact,first,last)
        shown=set()
        for no,f in enumerate(self.links):
            points,first,last=all_paths[no];self.draw_edge(no,f,points)
            for name,card,endpoint in [(f['a'],f['ca'],first),(f['b'],f['cb'],last)]:
                point,stub,side=endpoint;box=self.label_box(point,side)
                key=(name,card,box)
                if key not in shown:
                    self.text(card,*box,17 if self.physical else 18,False,align='center');shown.add(key)
            self.routes.append((f,points))

    def draw_edge(self,no,f,points):
        a,b=self.nodes[f['a']],self.nodes[f['b']]
        style='edgeStyle=none;noEdgeStyle=1;rounded=0;html=0;startArrow=none;endArrow=none;strokeColor=#555555;strokeWidth=1.3;'
        for n,p,pre in [(a,points[0],'exit'),(b,points[-1],'entry')]:
            x,y,w,h=n['box'];style+=f'{pre}X={(p[0]-x)/w};{pre}Y={(p[1]-y)/h};{pre}Perimeter=0;'
        c=ET.SubElement(self.root,'mxCell',id=f'e{no}',value='',style=style,edge='1',parent='1',source=a['id'],target=b['id'],sourceCardinality=f['ca'],targetCardinality=f['cb'],foreignKey=f['field'] or '',referencedColumn=f['parent_field'] or '',relationship=f['role'])
        g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
        arr=ET.SubElement(g,'Array',attrib={'as':'points'})
        for x,y in points[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))

    def save(self):
        items=list(self.nodes.items())
        for i,(name,node) in enumerate(items):
            for other,on in items[i+1:]:assert not intersects(node['box'],on['box']),(name,other)
        for f,points in self.routes:
            for a,b in zip(points,points[1:]):
                assert a[0]==b[0] or a[1]==b[1]
                for name,node in items:
                    assert not line_hits(a,b,node['box']),('edge through entity',f,name,a,b)
                for text,box in self.labels:assert not line_hits(a,b,box),('edge through text',text,f)
        for i,(label,box) in enumerate(self.labels):
            for name,n in items:assert not intersects(box,n['box']),('label/entity',label,name)
            for other,ob in self.labels[i+1:]:assert not intersects(box,ob),('label/label',label,other,box,ob)
        ET.indent(self.doc);path=BASE/(self.slug+'.drawio');ET.ElementTree(self.doc).write(path,encoding='utf-8',xml_declaration=True)
        root=ET.parse(path);cells=root.findall('.//mxCell');ids={c.get('id') for c in cells}
        assert len(ids)==len(cells)
        for c in cells:
            for k in ['parent','source','target']:
                if c.get(k):assert c.get(k) in ids
        crossings=set()
        for i,(_,one) in enumerate(self.routes):
            for _,two in self.routes[i+1:]:
                for a,b in zip(one,one[1:]):
                    for c,d in zip(two,two[1:]):
                        for u,v,r,s in [(a,b,c,d),(c,d,a,b)]:
                            if u[0]==v[0] and r[1]==s[1] and min(r[0],s[0])<u[0]<max(r[0],s[0]) and min(u[1],v[1])<r[1]<max(u[1],v[1]):crossings.add((u[0],r[1]))
        return {'file':path.name,'cells':len(cells),'relationships':len(self.links),'entity_boxes':len(self.nodes),'xml':'PASS','geometry':'PASS','text_fit':'PASS','routes_through_boxes_or_labels':0,'proper_crossing_locations':len(crossings),'notation':'explicit min..max cardinality at each relationship endpoint'}


def physical(model):
    d=Diagram('fmcg_physical_erd','FMCG Sales Intelligence — Physical PostgreSQL ERD',3400,2260,True)
    d.text('Operational schema fmcg | All declared columns, PK / FK / UNIQUE and SQL nullability | Print: A3 landscape',50,78,3100,30,22)
    for x,title in [(60,'CATALOG'),(880,'RETAIL / INVENTORY'),(1700,'PRICING / PROMOTIONS / DEMAND'),(2520,'ORDERS / DELIVERIES / SALES')]:d.text(title,x+60,115,650,28,21,True)
    positions={'categories':(60,175),'brands':(60,405),'products':(60,705),'skus':(60,1050),
        'regions':(880,175),'stores':(880,435),'warehouses':(880,875),'inventory':(880,1225),
        'promotions':(1700,175),'promotion_skus':(1700,605),'promotion_stores':(1700,835),'product_prices':(1700,1065),'daily_demand':(1700,1490),
        'orders':(2520,175),'order_items':(2520,705),'deliveries':(2520,1090),'delivery_items':(2520,1480),'sales':(2520,1730)}
    # Keep the final sales table above the A3 footer by tightening the transactional stack.
    positions.update(orders=(2520,175),order_items=(2520,665),deliveries=(2520,1015),delivery_items=(2520,1380),sales=(2520,1595))
    positions={k:(x+60,y) for k,(x,y) in positions.items()}
    checks={'skus':['CHECK: volume_ml > 0; units_per_case > 0','CHECK: 0 <= standard_cost <= base_price'],
        'promotions':['CHECK: end_date >= start_date','CHECK: percentage discount <= 100'],
        'product_prices':['CHECK: valid_to >= valid_from','CHECK: 0 <= selling_price <= regular_price'],
        'orders':['CHECK: delivery dates >= order_date','CHECK: total = subtotal - discount (summary)'],
        'order_items':['CHECK: quantity > 0; line_total >= 0'],
        'deliveries':['CHECK: delivered_at >= shipped_at, when set'],
        'delivery_items':['CHECK: quantity > 0'],
        'inventory':['CHECK: reserved_quantity <= stock_quantity','CHECK: stock flow and demand balance'],
        'sales':['CHECK: revenue and gross profit balance'],
        'daily_demand':['CHECK: requested = realized + lost (summary)','CHECK: censored = (lost > 0) (summary)']}
    for name,t in model['tables'].items():
        rows=[]
        for c in t['columns']:
            marks=[]
            if c['name'] in t['primary_key']:marks.append('PK')
            if any(f['column']==c['name'] for f in t['foreign_keys']):marks.append('FK')
            marks.extend('U'+str(i+1) for i,u in enumerate(t['unique']) if c['name'] in u)
            if c['generated_stored']:marks.append('G')
            rows.append(('/'.join(marks),c['name'],c['type'],'NL' if c['nullable'] else 'NN'))
        d.box(name,*positions[name],650,rows,checks.get(name,()))
    for child,t in model['tables'].items():
        for f in t['foreign_keys']:d.link(child,f['parent'],f['child_end'],f['parent_end'],f['column'],f['parent_column'],f"{child}.{f['column']} → {f['parent']}.{f['parent_column']}")
    d.text('PK: primary key | FK: foreign key | U1/U2: columns of the same UNIQUE constraint (within a table) | NN: NOT NULL | NL: nullable | G: generated stored',50,2135,3100,30,21)
    d.text('Cardinality at each endpoint: 1 = exactly one; 0..1 = optional one; 0..N = zero or many. Lines connect the actual FK and referenced key rows.',50,2174,3100,30,21)
    d.text('Composite PKs: promotion_skus, promotion_stores, delivery_items. No streaming, MLflow database or DuckDB/dbt tables are included.',50,2213,3100,30,21)
    d.text('PostgreSQL enum types\nprovenance_kind: public_factual,\ntransformed_external, synthetic\norder_status: created, confirmed, shipped,\ndelivered, cancelled\ndelivery_status: planned, shipped, delivered,\nfailed, cancelled',65,1540,620,230,22)
    d.route_all();return d.save()


def logical(entities,links):
    d=Diagram('fmcg_logical_erd','FMCG Sales Intelligence — Logical Domain Model',2500,1660,False)
    d.text('Business identities, meaningful attributes and relationships | Promotion eligibility is modeled as N:M | No SQL implementation details',50,77,2250,30,22)
    positions={'Category':(60,180),'Brand':(550,180),'Product':(280,475),'SKU':(280,820),
        'Region':(1040,180),'Store':(1530,180),'Promotion':(2020,180),'Product Price':(1920,570),
        'Warehouse':(830,580),'Order':(1330,585),'Order Item':(1330,980),'Sale':(1830,960),
        'Demand Observation':(1920,1310),'Inventory Snapshot':(840,1100),'Delivery':(60,1230),'Delivery Item':(530,1335)}
    attrs={
        'Category':['Category ID','Name','Description'],
        'Brand':['Brand ID','Name','Manufacturer'],
        'Product':['Product ID','Name','Sugar-free indicator'],
        'SKU':['SKU ID / SKU code','Flavor; package; volume','Units per case','Base price / standard cost'],
        'Region':['Region ID','Name / country'],
        'Store':['Store ID / external code','Name / city','Store type / channel'],
        'Warehouse':['Warehouse ID / code','Name / city','Capacity'],
        'Promotion':['Promotion ID','Name / type','Active date range','Discount type / value'],
        'Product Price':['Price ID','Effective date range','Regular / selling price'],
        'Order':['Order ID / order code','Order / delivery dates','Status','Subtotal / discount / total'],
        'Order Item':['Order Item ID','Quantity / unit price','Discount / line total'],
        'Delivery':['Delivery ID / code','Shipment / arrival times','Status'],
        'Delivery Item':['Delivery + SKU (identifier)','Quantity'],
        'Inventory Snapshot':['Inventory ID / date','Stock / reserved / available','Reorder / safety stock','Replenishment / lost sales'],
        'Sale':['Sale ID / date','Quantity / price / cost','Revenue / profit'],
        'Demand Observation':['Observation ID / date','Requested / realized / lost','Stock before observation','Inventory censoring'],
    }
    assert set(attrs)==set(entities)
    for name,rows in attrs.items():d.box(name,*positions[name],320,rows)
    for a,b,role,ca,cb in links:
        if (a,b) in [('Order','Order Item'),('Delivery','Delivery Item')]:cb='0..N'
        if role=='influences':role='associated with'
        d.link(a,b,ca,cb,role=role)
    d.text('Cardinality beside an entity: 1 = exactly one; 0..1 = optional one; 0..N = zero or many. Both ends 0..N denote N:M.',50,1580,2250,28,22)
    d.text('Daily sales, demand observations and inventory snapshots are distinct business records. A delivery may exist without an order.',50,1618,2250,28,22)
    d.route_all();return d.save()
