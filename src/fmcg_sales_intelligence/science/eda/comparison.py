from __future__ import annotations
from typing import Any
from .errors import IncompatibleRunsError
from .models import EDAResult,Finding,RunComparison,Severity

def _flat(data:dict[str,Any],prefix="")->dict[str,float]:
    out={}
    for k,v in data.items():
        key=f"{prefix}.{k}" if prefix else k
        if isinstance(v,dict):out.update(_flat(v,key))
        elif isinstance(v,(int,float)) and not isinstance(v,bool):out[key]=float(v)
    return out

def compare_runs(a:EDAResult,b:EDAResult)->RunComparison:
    if a.analysis_type!=b.analysis_type:raise IncompatibleRunsError(f"Cannot compare {a.analysis_type} with {b.analysis_type}")
    sa=a.datasets[0].schema if a.datasets else {};sb=b.datasets[0].schema if b.datasets else {}
    schema={"added_columns":sorted(set(sb)-set(sa)),"removed_columns":sorted(set(sa)-set(sb)),"dtype_changes":{k:{"old":sa[k],"new":sb[k]} for k in set(sa)&set(sb) if sa[k]!=sb[k]}}
    fa,fb=_flat(a.metrics),_flat(b.metrics);changes={}
    for k in sorted(set(fa)&set(fb)):
        old,new=fa[k],fb[k];changes[k]={"old":old,"new":new,"absolute_delta":new-old,"relative_delta":(new-old)/abs(old) if old else None}
    identical=len(a.datasets)==len(b.datasets) and all(x.content_sha256==y.content_sha256 for x,y in zip(a.datasets,b.datasets))
    findings=[]
    if any(schema.values()):findings.append(Finding("SCHEMA_CHANGED",Severity.WARNING,"Dataset schema changed.",evidence=schema))
    return RunComparison(a.run_id,b.run_id,a.analysis_type,identical,schema,changes,findings)
