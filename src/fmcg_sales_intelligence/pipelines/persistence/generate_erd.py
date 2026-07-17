"""Generate Mermaid and editable Draw.io ERDs from the live fmcg PostgreSQL schema."""
from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import html,json,re
from datetime import datetime,timezone
from pathlib import Path
from xml.etree.ElementTree import Element,SubElement,ElementTree
from fmcg_sales_intelligence.pipelines.persistence.connection import connect

ROOT = PROJECT_ROOT; DOCS=ROOT/"docs"
EXPECTED={"categories","brands","products","skus","regions","stores","warehouses","promotions","promotion_skus","promotion_stores","product_prices","sales","daily_demand","orders","order_items","deliveries","delivery_items","inventory"}
DOMAIN={
 "PRODUCT MASTER":["categories","brands","products","skus"],
 "LOCATION / DISTRIBUTION":["regions","stores","warehouses"],
 "PROMOTIONS":["promotions","promotion_skus","promotion_stores"],
 "PRICING":["product_prices"],"SALES":["sales","daily_demand"],
 "ORDERS / DELIVERIES":["orders","order_items","deliveries","delivery_items"],
 "INVENTORY":["inventory"]}
POSITION={
 "categories":(40,120),"brands":(40,430),"products":(380,220),"skus":(730,220),
 "regions":(1110,120),"stores":(1110,400),"warehouses":(1450,120),
 "promotions":(40,820),"promotion_skus":(380,760),"promotion_stores":(380,1040),
 "product_prices":(730,680),"sales":(730,1050),"daily_demand":(380,1050),"inventory":(1450,430),
 "orders":(1110,800),"order_items":(1450,800),"deliveries":(1110,1160),"delivery_items":(1450,1160)}
COLORS={"PRODUCT MASTER":"#dbeafe","LOCATION / DISTRIBUTION":"#dcfce7","PROMOTIONS":"#fef3c7","PRICING":"#ede9fe","SALES":"#fee2e2","ORDERS / DELIVERIES":"#e0f2fe","INVENTORY":"#fce7f3"}

def introspect():
    with connect() as conn,conn.cursor() as cur:
        cur.execute("""SELECT c.relname,a.attnum,a.attname,format_type(a.atttypid,a.atttypmod),a.attnotnull,
          COALESCE(string_agg(DISTINCT CASE co.contype WHEN 'p' THEN 'PK' WHEN 'u' THEN 'UK' END,',' ORDER BY CASE co.contype WHEN 'p' THEN 'PK' WHEN 'u' THEN 'UK' END),'') keys
          FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped
          LEFT JOIN pg_constraint co ON co.conrelid=c.oid AND co.contype IN('p','u') AND a.attnum=ANY(co.conkey)
          WHERE n.nspname='fmcg' AND c.relkind='r' GROUP BY c.relname,a.attnum,a.attname,a.atttypid,a.atttypmod,a.attnotnull ORDER BY c.relname,a.attnum""")
        tables={}
        for table,position,name,dtype,notnull,keys in cur.fetchall():tables.setdefault(table,[]).append({"position":position,"name":name,"type":dtype,"nullable":not notnull,"keys":[x for x in keys.split(',') if x]})
        cur.execute("""SELECT co.conname,child.relname,ca.attname,parent.relname,pa.attname,NOT ca.attnotnull
          FROM pg_constraint co JOIN pg_namespace n ON n.oid=co.connamespace JOIN pg_class child ON child.oid=co.conrelid JOIN pg_class parent ON parent.oid=co.confrelid
          JOIN LATERAL unnest(co.conkey,co.confkey) WITH ORDINALITY k(ca,pa,ord) ON true
          JOIN pg_attribute ca ON ca.attrelid=child.oid AND ca.attnum=k.ca JOIN pg_attribute pa ON pa.attrelid=parent.oid AND pa.attnum=k.pa
          WHERE n.nspname='fmcg' AND co.contype='f' ORDER BY child.relname,co.conname,k.ord""")
        fks=[{"constraint":a,"child_table":b,"child_column":c,"parent_table":d,"parent_column":e,"nullable":f} for a,b,c,d,e,f in cur.fetchall()]
        cur.execute("SHOW server_version");version=cur.fetchone()[0]
        cur.execute("""SELECT c.relname,co.conname,co.contype,pg_get_constraintdef(co.oid)
          FROM pg_constraint co JOIN pg_class c ON c.oid=co.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace
          WHERE n.nspname='fmcg' AND co.contype IN('p','u') ORDER BY c.relname,co.contype,co.conname""")
        business_keys=[{"table":a,"constraint":b,"kind":"PK" if c=="p" else "UK","definition":d} for a,b,c,d in cur.fetchall()]
    if set(tables)!=EXPECTED:raise RuntimeError(f"Table mismatch: expected={sorted(EXPECTED)} actual={sorted(tables)}")
    for fk in fks:
        next(c for c in tables[fk["child_table"]] if c["name"]==fk["child_column"])["keys"].append("FK")
    return {"generated_at":datetime.now(timezone.utc).isoformat(),"database":"fmcg","schema":"fmcg","postgresql_version":version,"tables":tables,"foreign_keys":fks,"business_keys":business_keys}

def mermaid(meta):
    lines=["# Operational PostgreSQL ERD","",f"Generated from live PostgreSQL `{meta['database']}.fmcg` metadata on `{meta['generated_at']}`. PostgreSQL `{meta['postgresql_version']}`.","","Logical domains: " + "; ".join(f"**{d}** — {', '.join(ts)}" for d,ts in DOMAIN.items()) + ".","","```mermaid","erDiagram"]
    for table,cols in meta["tables"].items():
        lines.append(f"    {table.upper()} {{")
        for c in cols:
            dtype=re.sub(r"[^A-Za-z0-9_]","_",c["type"]).strip("_")
            keys=", ".join(dict.fromkeys(c["keys"]));suffix=f" {keys}" if keys else ""
            null="nullable" if c["nullable"] else "not_null"
            lines.append(f"        {dtype} {c['name']}{suffix} \"{null}\"")
        lines.append("    }")
    for fk in meta["foreign_keys"]:
        parent=fk["parent_table"].upper();child=fk["child_table"].upper();child_side="o{" if fk["nullable"] else "|{"
        lines.append(f"    {parent} ||--{child_side} {child} : \"{fk['child_column']} → {fk['parent_column']}\"")
    lines += ["```","","Legend: **PK** = Primary Key; **FK** = Foreign Key; **UK** = Unique/business key. On multi-column constraints, UK marks participation in the composite key. `not_null` and `nullable` reflect live column metadata.","","## Implemented primary and unique keys","","| Table | Kind | PostgreSQL definition |","|---|---|---|"]
    lines += [f"| `{x['table']}` | {x['kind']} | `{x['definition']}` |" for x in meta["business_keys"]]
    lines += ["",f"Verified coverage: **{len(meta['tables'])} tables**, **{len(meta['foreign_keys'])} foreign-key relationships**. Each relationship above corresponds to exactly one live PostgreSQL FK constraint; no additional conceptual relationships are included.",""]
    return "\n".join(lines)

def drawio(meta,path):
    mx=Element("mxfile",{"host":"app.diagrams.net","modified":meta["generated_at"],"agent":"Codex PostgreSQL metadata generator","version":"24.7.17","type":"device"})
    diagram=SubElement(mx,"diagram",{"id":"fmcg-operational-erd","name":"FMCG Operational ERD"})
    model=SubElement(diagram,"mxGraphModel",{"dx":"1900","dy":"1450","grid":"1","gridSize":"10","guides":"1","tooltips":"1","connect":"1","arrows":"1","fold":"1","page":"1","pageScale":"1","pageWidth":"1900","pageHeight":"1500","math":"0","shadow":"0"})
    root=SubElement(model,"root");SubElement(root,"mxCell",{"id":"0"});SubElement(root,"mxCell",{"id":"1","parent":"0"})
    title=SubElement(root,"mxCell",{"id":"TITLE","value":"FMCG Sales Intelligence — Operational PostgreSQL ERD","style":"text;html=1;strokeColor=none;fillColor=none;align=center;fontSize=22;fontStyle=1;fontColor=#1f2937;","parent":"1","vertex":"1"});SubElement(title,"mxGeometry",{"x":"550","y":"20","width":"800","height":"40","as":"geometry"})
    subtitle=SubElement(root,"mxCell",{"id":"SUBTITLE","value":html.escape(f"Live schema: fmcg | PostgreSQL {meta['postgresql_version']} | {len(meta['tables'])} tables | {len(meta['foreign_keys'])} foreign keys"),"style":"text;html=1;strokeColor=none;fillColor=none;align=center;fontSize=12;fontColor=#64748b;","parent":"1","vertex":"1"});SubElement(subtitle,"mxGeometry",{"x":"600","y":"60","width":"700","height":"25","as":"geometry"})
    for i,(domain,tables) in enumerate(DOMAIN.items()):
        xs=[POSITION[t][0] for t in tables];ys=[POSITION[t][1] for t in tables]
        label=SubElement(root,"mxCell",{"id":f"DOMAIN_{i}","value":domain,"style":f"rounded=1;whiteSpace=wrap;html=1;fillColor={COLORS[domain]};strokeColor=#94a3b8;dashed=1;opacity=35;verticalAlign=top;align=left;spacingLeft=10;spacingTop=5;fontStyle=1;fontColor=#334155;","parent":"1","vertex":"1"})
        SubElement(label,"mxGeometry",{"x":str(min(xs)-15),"y":str(min(ys)-35),"width":str(max(xs)-min(xs)+335),"height":str(max(ys)-min(ys)+340),"as":"geometry"})
    table_domain={t:d for d,ts in DOMAIN.items() for t in ts}
    for table,cols in meta["tables"].items():
        rows=[]
        for c in cols:
            keys="/".join(dict.fromkeys(c["keys"]));prefix=f"<b>{keys}</b> " if keys else ""
            rows.append(f"<div style='text-align:left'>{prefix}{html.escape(c['name'])} <font color='#64748b'>{html.escape(c['type'])}</font></div>")
        value=f"<div style='font-size:14px;font-weight:bold;text-align:center'>{table}</div><hr/>"+"".join(rows)
        x,y=POSITION[table];height=54+22*len(cols)
        cell=SubElement(root,"mxCell",{"id":f"T_{table}","value":value,"style":f"rounded=1;whiteSpace=wrap;html=1;fillColor={COLORS[table_domain[table]]};strokeColor=#475569;strokeWidth=1.5;align=left;verticalAlign=top;spacing=8;fontSize=11;shadow=1;","parent":"1","vertex":"1"});SubElement(cell,"mxGeometry",{"x":str(x),"y":str(y),"width":"300","height":str(height),"as":"geometry"})
    for i,fk in enumerate(meta["foreign_keys"]):
        edge=SubElement(root,"mxCell",{"id":f"FK_{i}","value":fk["child_column"],"style":"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;startArrow=ERmany;startFill=0;endArrow=ERone;endFill=0;strokeColor=#64748b;fontSize=9;labelBackgroundColor=#ffffff;","parent":"1","source":f"T_{fk['child_table']}","target":f"T_{fk['parent_table']}","edge":"1"});SubElement(edge,"mxGeometry",{"relative":"1","as":"geometry"})
    legend=SubElement(root,"mxCell",{"id":"LEGEND","value":"<b>Legend</b><br/>PK = Primary Key &nbsp; FK = Foreign Key &nbsp; UK = Unique/business key<br/>UK on multiple rows denotes participation in a composite key. Crow's foot = many; bar = one.","style":"rounded=1;whiteSpace=wrap;html=1;fillColor=#f8fafc;strokeColor=#94a3b8;align=left;spacing=8;fontSize=11;","parent":"1","vertex":"1"});SubElement(legend,"mxGeometry",{"x":"40","y":"1390","width":"700","height":"70","as":"geometry"})
    ElementTree(mx).write(path,encoding="utf-8",xml_declaration=True)

def verify(meta,mermaid_text,drawio_path):
    mermaid_edges={(m.group(1).lower(),m.group(3),m.group(2).lower(),m.group(4)) for m in re.finditer(r'^\s*([A-Z_]+) \|\|--[o|]\{ ([A-Z_]+) : "([^\"]+) → ([^\"]+)"',mermaid_text,re.M)}
    expected={(f["parent_table"],f["child_column"],f["child_table"],f["parent_column"]) for f in meta["foreign_keys"]}
    # normalize Mermaid capture order: parent, child-column label, child, parent-column
    if mermaid_edges!=expected:raise RuntimeError(f"Mermaid FK mismatch: missing={expected-mermaid_edges}, extra={mermaid_edges-expected}")
    xml=Path(drawio_path).read_text(encoding="utf-8")
    if xml.count('id="FK_')!=len(expected):raise RuntimeError("Draw.io FK edge count mismatch")
    return {"tables":len(meta["tables"]),"foreign_keys":len(expected),"mermaid_verified":True,"drawio_verified":True}

def main():
    meta=introspect();DOCS.mkdir(exist_ok=True);metadata_path=DOCS/"erd_metadata.json";metadata_path.write_text(json.dumps(meta,indent=2),encoding="utf-8")
    text=mermaid(meta);(DOCS/"erd.md").write_text(text,encoding="utf-8")
    source=text.split("```mermaid\n",1)[1].split("\n```",1)[0]+"\n";(DOCS/"erd.mmd").write_text(source,encoding="utf-8")
    drawio(meta,DOCS/"erd.drawio")
    result=verify(meta,text,DOCS/"erd.drawio");(DOCS/"erd_verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
