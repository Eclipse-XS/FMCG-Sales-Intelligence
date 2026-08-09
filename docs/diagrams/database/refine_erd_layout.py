"""Layout-only XML transformation. Source documents are never overwritten.

The input graph and all text/semantic attributes come from existing .drawio files.
Placement candidates are optional Graphviz neato JSON exports, not model sources.
"""
import argparse
import collections
import copy
import hashlib
import heapq
import itertools
import json
import math
from pathlib import Path
import random
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
CARDS = {'1', '0..1', '0..N'}


def style(c):
    return dict(s.split('=', 1) for s in c.get('style', '').split(';') if '=' in s)


def box(c):
    g = c.find('mxGeometry')
    return tuple(float(g.get(k, 0)) for k in ('x', 'y', 'width', 'height'))


def overlap(a, b):
    x, y, w, h = a; u, v, r, s = b
    return max(x, u) < min(x+w, u+r) and max(y, v) < min(y+h, v+s)


def hits(a, b, r):
    x, y, w, h = r
    return ((a[0] == b[0] and x < a[0] < x+w and max(min(a[1], b[1]), y) < min(max(a[1], b[1]), y+h)) or
            (a[1] == b[1] and y < a[1] < y+h and max(min(a[0], b[0]), x) < min(max(a[0], b[0]), x+w)))


def simplify(points):
    pts = []
    for p in points:
        if pts and p == pts[-1]:
            continue
        while len(pts) > 1 and ((pts[-2][0] == pts[-1][0] == p[0]) or (pts[-2][1] == pts[-1][1] == p[1])):
            pts.pop()
        pts.append(p)
    return pts


def geometry_metrics(nodes, routes, labels):
    crossings = set(); through = []; covered = []; shared = 0
    lengths = {}; bends = {}
    segments = []
    for eid, pts in routes.items():
        lengths[eid] = sum(abs(a[0]-b[0])+abs(a[1]-b[1]) for a, b in zip(pts, pts[1:]))
        bends[eid] = max(0, len(simplify(pts))-2)
        for a, b in zip(pts, pts[1:]):
            assert a[0] == b[0] or a[1] == b[1], (eid, a, b)
            for name, r in nodes.items():
                if hits(a, b, r): through.append((eid, name))
            for lid, r in labels.items():
                if hits(a, b, r): covered.append((eid, lid))
            segments.append((eid, a, b))
    for i, (eid, a, b) in enumerate(segments):
        for other, c, d in segments[i+1:]:
            if eid == other: continue
            for u, v, r, s in [(a, b, c, d), (c, d, a, b)]:
                if u[0] == v[0] and r[1] == s[1] and min(r[0], s[0]) < u[0] < max(r[0], s[0]) and min(u[1], v[1]) < r[1] < max(u[1], v[1]):
                    crossings.add((u[0], r[1]))
            if a[0] == b[0] == c[0] == d[0]:
                shared += max(0, min(max(a[1], b[1]), max(c[1], d[1])) - max(min(a[1], b[1]), min(c[1], d[1])))
            if a[1] == b[1] == c[1] == d[1]:
                shared += max(0, min(max(a[0], b[0]), max(c[0], d[0])) - max(min(a[0], b[0]), min(c[0], d[0])))
    ns = list(nodes.items()); ls = list(labels.items())
    return {'crossings': len(crossings), 'crossing_points': sorted(crossings),
            'route_length': round(sum(lengths.values())), 'longest_route': round(max(lengths.values())),
            'route_lengths': lengths, 'bends': bends, 'maximum_bends': max(bends.values()),
            'shared_segment_length_pair_sum': round(shared),
            'connectors_through_boxes': sorted(set(through)), 'connectors_through_labels': sorted(set(covered)),
            'box_overlaps': [(a, b) for i, (a, r) in enumerate(ns) for b, s in ns[i+1:] if overlap(r, s)],
            'label_overlaps': [(a, b) for i, (a, r) in enumerate(ls) for b, s in ls[i+1:] if overlap(r, s)],
            'label_box_overlaps': [(a, b) for a, r in ls for b, s in ns if overlap(r, s)]}


class ExistingDiagram:
    def __init__(self, kind):
        self.kind = kind; self.path = BASE / f'fmcg_{kind}_erd.drawio'
        self.doc = ET.parse(self.path); self.original = copy.deepcopy(self.doc)
        self.model = self.doc.find('.//mxGraphModel'); self.cells = self.doc.findall('.//mxCell')
        self.nodes = {c.get('id'): c for c in self.cells if c.get('entity')}
        self.edges = {c.get('id'): c for c in self.cells if c.get('edge') == '1'}
        self.labels = {c.get('id'): c for c in self.cells if c.get('parent') == '1' and c.get('value') in CARDS}
        self.other_text = [c for c in self.cells if c.get('parent') == '1' and c.get('vertex') == '1' and not c.get('entity') and c.get('id') not in self.labels]
        self.original_boxes = {i: box(c) for i, c in self.nodes.items()}
        self.ends = {}; self.groups = collections.defaultdict(lambda: {'refs': [], 'labels': []})
        for eid, e in self.edges.items():
            st = style(e)
            for end, attr, anchor, cardinality in [(0, 'source', 'exit', 'sourceCardinality'), (1, 'target', 'entry', 'targetCardinality')]:
                nid = e.get(attr); x, y, w, h = self.original_boxes[nid]
                dy = round(float(st[anchor+'Y'])*h, 6)
                point = (x + float(st[anchor+'X'])*w, y+dy)
                key = (nid, dy, e.get(cardinality))
                ref = (eid, end)
                self.ends[ref] = {'node': nid, 'dy': dy, 'card': e.get(cardinality), 'point': point, 'group': key}
                self.groups[key]['refs'].append(ref)
        for lid, c in self.labels.items():
            x, y, w, h = box(c)
            candidates = [(abs((x+w/2)-d['point'][0]) + abs((y+h+4)-d['point'][1]), d['group'])
                          for d in self.ends.values() if d['card'] == c.get('value')]
            _, key = min(candidates)
            self.groups[key]['labels'].append(lid)
        assert all(g['labels'] for g in self.groups.values())
        self.before_routes = self.read_routes()
        self.before = geometry_metrics(self.original_boxes, self.before_routes, {i: box(c) for i, c in self.labels.items()})
        self.degree = collections.Counter()
        for e in self.edges.values(): self.degree[e.get('source')] += 1; self.degree[e.get('target')] += 1

    def read_routes(self):
        routes = {}
        for eid, e in self.edges.items():
            st = style(e); points = []
            for side, anchor in [('source', 'exit'), ('target', 'entry')]:
                x, y, w, h = box(self.nodes[e.get(side)])
                points.append((round(x+w*float(st[anchor+'X']), 6), round(y+h*float(st[anchor+'Y']), 6)))
            routes[eid] = [points[0]] + [(float(p.get('x')), float(p.get('y'))) for p in e.findall('.//mxPoint')] + [points[1]]
        return routes

    def place(self, candidate):
        data = json.loads(Path(candidate).read_text())
        W, H = map(float, data['bb'].split(',')[2:])
        # Reflect horizontally: catalog leaves move to the left, hubs stay central.
        for n in data['objects']:
            nid = n['name']; cx, cy = map(float, n['pos'].split(','))
            _, _, w, h = self.original_boxes[nid]
            x = round((W-cx-w/2)/20)*20+160
            y = round((H-cy-h/2)/20)*20+230
            g = self.nodes[nid].find('mxGeometry'); g.set('x', str(x)); g.set('y', str(y))
        self.boxes = {i: box(c) for i, c in self.nodes.items()}
        catalog=[b[0] for i,b in self.boxes.items() if self.nodes[i].get('entity').lower() in ('category','brand','product','categories','brands','products')]
        span=max(x+w for x,y,w,h in self.boxes.values())+160
        if sum(catalog)/len(catalog)>span/2:
            for i,(x,y,w,h) in self.boxes.items():self.nodes[i].find('mxGeometry').set('x',str(span-x-w))
            self.boxes = {i: box(c) for i, c in self.nodes.items()}
        self.width = math.ceil((max(x+w for x, y, w, h in self.boxes.values())+180)/20)*20
        self.height = math.ceil((max(y+h for x, y, w, h in self.boxes.values())+330)/20)*20
        if self.height > self.width: self.width = math.ceil(self.height*1.2/20)*20
        self.model.set('pageWidth', str(self.width)); self.model.set('pageHeight', str(self.height))
        # Preserve every existing annotation, moving cluster captions to a footer key.
        headings = []; notes = []; footers = []
        for c in self.other_text:
            x, y, w, h = box(c)
            if y < 110: continue
            if self.kind == 'physical' and y < 150: headings.append(c)
            elif c.get('value', '').startswith('PostgreSQL enum types'): notes.append(c)
            else: footers.append(c)
        bottom = max(y+h for x, y, w, h in self.boxes.values())+85
        for i, c in enumerate(headings):
            g=c.find('mxGeometry'); g.set('x',str(60+i*(self.width-120)/4));g.set('y',str(bottom))
        for i, c in enumerate(footers):
            g=c.find('mxGeometry');g.set('x','50');g.set('y',str(bottom+50+i*39))
        for c in notes:
            # The enum note is retained in a reserved footer block.
            g=c.find('mxGeometry');g.set('x',str(self.width-690));g.set('y',str(bottom+45))
            self.height=max(self.height,math.ceil((bottom+300)/20)*20)
        self.model.set('pageHeight',str(self.height))

    def allocate_ports(self):
        self.ports = {}; self.label_boxes = {}
        if self.kind=='logical':
            for key,group in self.groups.items():
                nid,dy,card=key;x,y,w,h=self.boxes[nid]
                px=x+w*{'1':.25,'0..1':.5,'0..N':.75}[card]
                endpoints={'W':((x,y+dy),(-1,0)),'E':((x+w,y+dy),(1,0)),
                           'N':((px,y),(0,-1)),'S':((px,y+h),(0,1))}
                refs=group['refs'];lids=group['labels'];cost={}
                for ref in refs:
                    other=self.ends[ref[0],1-ref[1]]['node'];ox,oy,ow,oh=self.boxes[other]
                    dx=ox+ow/2-(x+w/2);ddy=oy+oh/2-(y+h/2)
                    for direction,(point,(sx,sy)) in endpoints.items():
                        cost[ref,direction]=abs(point[0]+sx*100-(ox+ow/2))+abs(point[1]+sy*100-(oy+oh/2))-180*(sx*dx+sy*ddy)/max(1,math.hypot(dx,ddy))
                        if other==nid:cost[ref,direction]=0 if direction=='W' else 2000
                best=None
                for dirs in itertools.combinations(endpoints,len(lids)):
                    assignments={direction:[] for direction in dirs}
                    for ref in refs:assignments[min(dirs,key=lambda direction:cost[ref,direction])].append(ref)
                    if any(not selected for selected in assignments.values()):continue
                    total=sum(cost[ref,direction] for direction,selected in assignments.items() for ref in selected)
                    if best is None or total<best[0]:best=(total,assignments)
                assert best is not None,key
                for lid,(direction,selected) in zip(lids,best[1].items()):
                    point,(sx,sy)=endpoints[direction];lh=box(self.labels[lid])[3]
                    if sx:lb=(point[0]-76 if sx<0 else point[0]+12,point[1]-27,64,lh)
                    else:lb=(point[0]+12,point[1]-lh-12 if sy<0 else point[1]+12,64,lh)
                    g=self.labels[lid].find('mxGeometry');g.set('x',str(lb[0]));g.set('y',str(lb[1]));self.label_boxes[lid]=lb
                    for ref in selected:self.ports[ref]=(point,(point[0]+sx*96,point[1]+sy*96),(sx,sy))
            return
        forced = {}
        # A nullable and mandatory reference to the same PK retain separate sides.
        by_row = collections.defaultdict(list)
        for key in self.groups: by_row[key[:2]].append(key)
        for keys in by_row.values():
            cards={k[2] for k in keys}
            if '0..1' in cards and '1' in cards:
                for k in keys: forced[k] = -1 if k[2] == '0..1' else 1
        for key, group in self.groups.items():
            nid, dy, card = key; x, y, w, h = self.boxes[nid]
            refs = group['refs']; lids = group['labels']
            ranked = []
            for ref in refs:
                other = self.ends[(ref[0], 1-ref[1])]['node']; ox, oy, ow, oh = self.boxes[other]
                ranked.append((ox+ow/2-(x+w/2), ref))
            ranked.sort()
            if len(lids) == 2:
                split = max(1, min(len(refs)-1, sum(delta<0 for delta, r in ranked)))
                assignments = [(lids[0], -1, [r for _, r in ranked[:split]]), (lids[1], 1, [r for _, r in ranked[split:]])]
            else:
                assert len(lids) == 1, (key, lids)
                side = forced.get(key, -1 if sum(delta for delta, r in ranked)<0 else 1)
                if all(self.edges[ref[0]].get('source')==self.edges[ref[0]].get('target') for ref in refs):side=-1
                assignments = [(lids[0], side, refs)]
            for lid, side, selected in assignments:
                assert selected, (key, assignments)
                point = (x if side<0 else x+w, y+dy)
                lb = (point[0]-76 if side<0 else point[0]+12, point[1]-27, 64, box(self.labels[lid])[3])
                g=self.labels[lid].find('mxGeometry');g.set('x',str(lb[0]));g.set('y',str(lb[1]))
                self.label_boxes[lid]=lb
                for ref in selected:
                    self.ports[ref]=(point, (point[0]+side*96,point[1]),side)
        assert len(self.ports)==2*len(self.edges)
        obstacles=list(self.boxes.values())+list(self.label_boxes.values())
        for ref,(point,stub,side) in list(self.ports.items()):
            candidates=sorted(range(84,161,2),key=lambda delta:abs(delta-96))
            for delta in candidates:
                s=(point[0]+side*delta,point[1])
                if not any(x-7<s[0]<x+w+7 and y-7<s[1]<y+h+7 for x,y,w,h in obstacles):
                    self.ports[ref]=(point,s,side);break

    def route(self, seed=0, crossing_cost=900, guides=None):
        obstacles=list(self.boxes.values())+list(self.label_boxes.values())
        xs=set(range(40,self.width-39,24));ys=set(range(150,self.height-249,24))
        for x,y,w,h in obstacles:
            xs.update([x-20,x+w+20]);ys.update([y-20,y+h+20])
        for p,s,side in self.ports.values():xs.add(s[0]);ys.add(s[1])
        xs=sorted(x for x in xs if 20<x<self.width-20);ys=sorted(y for y in ys if 120<y<self.height-250)
        xi={x:i for i,x in enumerate(xs)};yi={y:i for i,y in enumerate(ys)}
        free={};used={};directions={};routes={}
        def allowed(ix,iy):
            key=(ix,iy)
            if key not in free:
                x,y=xs[ix],ys[iy]
                free[key]=not any(a-7<x<a+w+7 and b-7<y<b+h+7 for a,b,w,h in obstacles)
            return free[key]
        # Reserve short endpoint leads so unrelated paths cannot occupy them.
        lead_segments = [(ref,p,s) for ref,(p,s,side) in self.ports.items()]
        for ref,p,s in lead_segments:
            if p[1]==s[1]:
                iy=yi[p[1]]
                for ix,x in enumerate(xs):
                    if min(p[0],s[0]) < x < max(p[0],s[0]):directions.setdefault((ix,iy),set()).add(0)
            else:
                ix=xi[p[0]]
                for iy,y in enumerate(ys):
                    if min(p[1],s[1]) < y < max(p[1],s[1]):directions.setdefault((ix,iy),set()).add(1)
        order=sorted(self.edges,key=lambda eid:abs(self.ports[eid,0][1][0]-self.ports[eid,1][1][0])+abs(self.ports[eid,0][1][1]-self.ports[eid,1][1][1]))
        if seed:random.Random(seed).shuffle(order)
        for eid in order:
            attraction={}
            guide=guides[eid] if guides else None
            def distance_from_guide(ix,iy):
                if guide is None:return 0
                key=(ix,iy)
                if key not in attraction:
                    x,y=xs[ix],ys[iy]
                    attraction[key]=min(max(min(a[0],b[0])-x,0,x-max(a[0],b[0]))+max(min(a[1],b[1])-y,0,y-max(a[1],b[1])) for a,b in zip(guide,guide[1:]))
                return attraction[key]
            first,last=self.ports[eid,0],self.ports[eid,1]
            start=(xi[first[1][0]],yi[first[1][1]]);goal=(xi[last[1][0]],yi[last[1][1]])
            sd=0 if first[0][1]==first[1][1] else 1
            q=[];dist={(*start,sd):0};travel={(*start,sd):0};prev={};heapq.heappush(q,(0,0,(*start,sd)))
            def heuristic(ix,iy):return abs(xs[ix]-xs[goal[0]])+abs(ys[iy]-ys[goal[1]])
            limit=2.1*heuristic(*start)+650
            final=None
            while q:
                _,cost,state=heapq.heappop(q)
                if cost!=dist.get(state):continue
                ix,iy,d=state
                if (ix,iy)==goal:final=state;break
                for dx,dy,nd in [(1,0,0),(-1,0,0),(0,1,1),(0,-1,1)]:
                    nx,ny=ix+dx,iy+dy
                    if not (0<=nx<len(xs) and 0<=ny<len(ys)) or not allowed(nx,ny):continue
                    a=(ix,iy);b=(nx,ny);ek=tuple(sorted((a,b)))
                    length=abs(xs[ix]-xs[nx])+abs(ys[iy]-ys[ny])
                    distance=travel[state]+length
                    if distance+heuristic(nx,ny)>limit:continue
                    penalty=length*(1+75*used.get(ek,0))+(110 if nd!=d else 0)
                    penalty+=length*distance_from_guide(nx,ny)*.045
                    if directions.get(b,set())-{nd}:penalty+=crossing_cost
                    ncost=cost+penalty;nstate=(nx,ny,nd)
                    if ncost<dist.get(nstate,float('inf')):
                        dist[nstate]=ncost;travel[nstate]=distance;prev[nstate]=state
                        heapq.heappush(q,(ncost+heuristic(nx,ny),ncost,nstate))
            assert final is not None,('route failed',eid,first,last,[(r,allowed(*r)) for r in [start,goal]],limit)
            path=[];state=final
            while True:
                path.append((state[0],state[1]))
                if state not in prev:break
                state=prev[state]
            path.reverse()
            for a,b in zip(path,path[1:]):
                ek=tuple(sorted((a,b)));used[ek]=used.get(ek,0)+1
                nd=0 if a[1]==b[1] else 1
                directions.setdefault(a,set()).add(nd);directions.setdefault(b,set()).add(nd)
            routes[eid]=simplify([first[0]]+[(xs[ix],ys[iy]) for ix,iy in path]+[last[0]])
        self.routes=routes
        return geometry_metrics(self.boxes,routes,self.label_boxes)

    def write(self, metrics):
        for eid,e in self.edges.items():
            pts=self.routes[eid];st=style(e)
            for end,nid,pre in [(0,e.get('source'),'exit'),(-1,e.get('target'),'entry')]:
                x,y,w,h=self.boxes[nid]
                st[pre+'X']=str((pts[end][0]-x)/w);st[pre+'Y']=str((pts[end][1]-y)/h)
            e.set('style',';'.join(k+'='+v for k,v in st.items())+';')
            g=e.find('mxGeometry')
            for child in list(g):g.remove(child)
            arr=ET.SubElement(g,'Array',attrib={'as':'points'})
            for x,y in pts[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        # Only geometry and connector anchor styling may differ from the input.
        original={c.get('id'):c for c in self.original.findall('.//mxCell')}
        assert set(original)=={c.get('id') for c in self.cells}
        for c in self.cells:
            old=original[c.get('id')]
            for k,v in old.attrib.items():
                if k=='style' and c.get('edge')=='1':
                    a=style(old);b=style(c)
                    for allowed in ['exitX','exitY','entryX','entryY']:a.pop(allowed,None);b.pop(allowed,None)
                    assert a==b
                else:assert c.get(k)==v,(c.get('id'),k)
            if c.get('edge')!='1':
                a=old.find('mxGeometry');b=c.find('mxGeometry')
                if a is not None:
                    assert {k:v for k,v in a.attrib.items() if k not in ('x','y')}=={k:v for k,v in b.attrib.items() if k not in ('x','y')}
        out=BASE/f'fmcg_{self.kind}_erd_readable_v2.drawio'
        ET.indent(self.doc);self.doc.write(out,encoding='utf-8',xml_declaration=True)
        ET.parse(out)
        return {'input':str(self.path),'output':str(out),'source_sha256':hashlib.sha256(self.path.read_bytes()).hexdigest(),
                'entities':len(self.nodes),'edges':len(self.edges),'cells_unchanged':len(self.cells),'semantic_attributes_and_text':'IDENTICAL',
                'original_box_sizes_fonts_and_styles':'IDENTICAL','xml_parse':'PASS','dangling_edges':0,
                'degrees':{self.nodes[i].get('entity'):v for i,v in self.degree.most_common()},
                'old_waypoints_replaced':sum(len(p)-2 for p in self.before_routes.values()),
                'new_waypoints':sum(len(p)-2 for p in self.routes.values()),'edges_rerouted':len(self.routes),
                'before':self.before,'after':metrics}

    def simplify_routes(self):
        """Remove avoidable doglegs without introducing new crossings or overlaps."""
        obstacles=list(self.boxes.values())+list(self.label_boxes.values())
        def edge_cost(points,others):
            crossings=set();shared=0
            for a,b in zip(points,points[1:]):
                for c,d in others:
                    for u,v,r,s in [(a,b,c,d),(c,d,a,b)]:
                        if u[0]==v[0] and r[1]==s[1] and min(r[0],s[0])<u[0]<max(r[0],s[0]) and min(u[1],v[1])<r[1]<max(u[1],v[1]):crossings.add((u[0],r[1]))
                    if a[0]==b[0]==c[0]==d[0]:shared+=max(0,min(max(a[1],b[1]),max(c[1],d[1]))-max(min(a[1],b[1]),min(c[1],d[1])))
                    if a[1]==b[1]==c[1]==d[1]:shared+=max(0,min(max(a[0],b[0]),max(c[0],d[0]))-max(min(a[0],b[0]),min(c[0],d[0])))
            length=sum(abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in zip(points,points[1:]))
            return len(crossings),shared,length+120*len(points)
        for repeat in range(3):
            changed=False
            for eid,points in list(self.routes.items()):
                others=[(a,b) for other,ps in self.routes.items() if other!=eid for a,b in zip(ps,ps[1:])]
                old=edge_cost(points,others);winner=None
                for i in range(len(points)-2):
                    for j in range(i+2,len(points)):
                        a,b=points[i],points[j]
                        for corner in [(a[0],b[1]),(b[0],a[1])]:
                            replacement=simplify([a,corner,b])
                            if any(hits(u,v,r) for u,v in zip(replacement,replacement[1:]) for r in obstacles):continue
                            trial=simplify(points[:i]+replacement+points[j+1:])
                            # Preserve the outward direction of endpoint leads.
                            def direction(a,b):return (0 if a[0]==b[0] else (1 if b[0]>a[0] else -1),0 if a[1]==b[1] else (1 if b[1]>a[1] else -1))
                            if direction(trial[0],trial[1])!=direction(points[0],points[1]) or direction(trial[-1],trial[-2])!=direction(points[-1],points[-2]):continue
                            score=edge_cost(trial,others)
                            if score[0]<=old[0] and score[1]<=old[1]+.01 and score[2]<old[2]-.01:
                                if winner is None or score<winner[0]:winner=(score,trial)
                if winner:self.routes[eid]=winner[1];changed=True
            if not changed:break
        return geometry_metrics(self.boxes,self.routes,self.label_boxes)


def main():
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['logical','physical']);p.add_argument('candidate',type=Path)
    p.add_argument('--seed',type=int,default=0);p.add_argument('--crossing-cost',type=int,default=900)
    args=p.parse_args();d=ExistingDiagram(args.kind);d.place(args.candidate);d.allocate_ports();m=d.route(args.seed,args.crossing_cost)
    report=d.write(m);(BASE/f'fmcg_{args.kind}_layout_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in m.items() if k not in ['route_lengths','bends','crossing_points']},indent=2))


if __name__=='__main__':main()
