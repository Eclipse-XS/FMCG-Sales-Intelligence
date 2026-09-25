"""Read the repository DDL, without connecting to or modifying PostgreSQL."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def split_top(text):
    parts=[]; start=depth=0; quoted=False
    for i,c in enumerate(text):
        if c=="'": quoted=not quoted
        if not quoted:
            if c=='(': depth+=1
            elif c==')': depth-=1
            elif c==',' and depth==0: parts.append(text[start:i].strip()); start=i+1
    parts.append(text[start:].strip())
    assert depth==0 and not quoted
    return parts


def parens(text,start):
    depth=0; quoted=False
    for i in range(start,len(text)):
        c=text[i]
        if c=="'": quoted=not quoted
        if not quoted:
            if c=='(': depth+=1
            elif c==')':
                depth-=1
                if depth==0:return text[start+1:i]
    raise ValueError(text)


def extract(sql):
    tables={}
    for m in re.finditer(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?([\w.]+)\s*\(',sql,re.I):
        name=m[1];body=parens(sql,m.end()-1)
        t={'columns':[],'primary_key':[],'unique':[],'foreign_keys':[],'checks':[]}
        for part in split_top(body):
            for chk in re.finditer(r'\bCHECK\s*\(',part,re.I):t['checks'].append(parens(part,chk.end()-1))
            if part.upper().startswith('PRIMARY KEY'):
                t['primary_key']=split_top(parens(part,part.index('(')));continue
            if part.upper().startswith('UNIQUE'):
                t['unique'].append(split_top(parens(part,part.index('('))));continue
            if part.upper().startswith('CHECK'):continue
            c=re.match(r'(\w+)\s+(\w+(?:\([^)]*\))?)(.*)',part,re.S)
            assert c,part
            column,typ,tail=c.groups()
            pk='PRIMARY KEY' in tail.upper()
            if pk:t['primary_key'].append(column)
            if re.search(r'\bUNIQUE\b',tail,re.I):t['unique'].append([column])
            col={'name':column,'type':typ,'nullable':not bool(re.search(r'NOT NULL|PRIMARY KEY',tail,re.I)),
                 'identity':'AS IDENTITY' in tail.upper(),'generated_stored':'STORED' in tail.upper(),'definition':part}
            gen=re.search(r'GENERATED ALWAYS AS\s*\(',tail,re.I)
            if gen:col['expression']=parens(tail,gen.end()-1)
            t['columns'].append(col)
            fk=re.search(r'REFERENCES\s+([\w.]+)\s*\((\w+)\)',tail,re.I)
            if fk:t['foreign_keys'].append({'column':column,'parent':fk[1],'parent_column':fk[2],
                'on_delete':'CASCADE' if re.search(r'ON DELETE CASCADE',tail,re.I) else 'NO ACTION','on_update':'NO ACTION'})
        for col in t['columns']:
            if col['name'] in t['primary_key']:col['nullable']=False
        for fk in t['foreign_keys']:
            fk['optional']=next(c['nullable'] for c in t['columns'] if c['name']==fk['column'])
            fk['parent_end']='0..1' if fk['optional'] else '1'
            fk['child_end']='0..1' if [fk['column']] in [t['primary_key']]+t['unique'] else '0..N'
        tables[name]=t
    return tables


def audit():
    path=ROOT/'platform/postgres/schema.sql';sql=path.read_text(encoding='utf-8')
    core=extract(sql)
    technical=extract((ROOT/'src/fmcg_sales_intelligence/pipelines/streaming/init_streaming.py').read_text(encoding='utf-8'))
    enums={m[1]:re.findall(r"'([^']*)'",m[2]) for m in re.finditer(r'CREATE TYPE (\w+) AS ENUM \((.*?)\);',sql)}
    for table,t in core.items():
        names={c['name'] for c in t['columns']}
        assert set(t['primary_key'])<=names
        for fk in t['foreign_keys']:
            parent=core[fk['parent']]
            assert [fk['parent_column']] in [parent['primary_key']]+parent['unique']
    result={'source':'platform/postgres/schema.sql','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'tables':core,'enums':enums,'technical_tables_excluded':technical,
            'performance_indexes':re.findall(r'CREATE INDEX\s+(\w+)',(ROOT/'platform/postgres/indexes.sql').read_text()),
            'counts':{'tables':len(core),'columns':sum(len(t['columns']) for t in core.values()),
                'foreign_keys':sum(len(t['foreign_keys']) for t in core.values()),'unique_constraints':sum(len(t['unique']) for t in core.values()),
                'checks':sum(len(t['checks']) for t in core.values())}}
    (BASE/'fmcg_schema_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':print(json.dumps(audit()['counts']))
