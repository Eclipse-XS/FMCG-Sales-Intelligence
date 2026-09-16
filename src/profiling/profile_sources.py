"""Bounded, reproducible profiler for CSV, Parquet and Excel sources."""
from __future__ import annotations
import hashlib, json, zipfile
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]; MAX_ROWS=250_000
URLS={
 "favorita":"https://www.kaggle.com/datasets/evgeniypolin/favorita-grocery-sales-forecasting",
 "m5":"https://doi.org/10.5281/zenodo.10203108",
 "online_retail_ii":"https://archive.ics.uci.edu/dataset/502/online+retail+ii",
 "instacart":"https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis",
 "dunnhumby":"https://github.com/bltap-plmarket/dunnhumby-complete-journey",
 "coca_cola_reference":"https://github.com/Chad-Lines/Data-Projects/tree/main/Coca-Cola%20Sales%20Data%20Visualiation",
}
def frame_profile(df):
    n=len(df); dates={}
    for c in df.columns:
        if any(k in str(c).lower() for k in ("date","time")):
            s=pd.to_datetime(df[c],errors="coerce")
            if s.notna().any(): dates[str(c)]={"min":str(s.min()),"max":str(s.max())}
    cols=[]
    for c in df.columns:
        unique=int(df[c].nunique(dropna=True)); item={"name":str(c),"dtype":str(df[c].dtype),"null_pct":round(float(df[c].isna().mean()*100),3),"unique":unique}
        if unique <= 30: item["important_values"]=[str(x) for x in df[c].value_counts(dropna=False).head(10).index]
        cols.append(item)
    candidate_keys=[str(c) for c in df.columns if n and df[c].notna().all() and df[c].nunique()==n]
    return {"profiled_rows":n,"columns":cols,"duplicate_rows":int(df.duplicated().sum()),"date_ranges":dates,"candidate_single_column_keys":candidate_keys,"profile_is_sample":n>=MAX_ROWS}
def read_file(path, member=None):
    suffix=Path(member or path.name).suffix.lower()
    if member:
        with zipfile.ZipFile(path) as z, z.open(member) as f:
            if suffix==".csv": return pd.read_csv(f,nrows=MAX_ROWS,low_memory=False)
            if suffix in (".xlsx",".xls"): return pd.read_excel(f,nrows=MAX_ROWS)
    if suffix==".csv": return pd.read_csv(path,nrows=MAX_ROWS,low_memory=False)
    if suffix in (".parquet",".pq"): return pd.read_parquet(path).head(MAX_ROWS)
    if suffix in (".xlsx",".xls"): return pd.read_excel(path,nrows=MAX_ROWS)
def main():
    registry_path=ROOT/"data/metadata/source_registry.json"
    registry={x["name"]:x for x in json.loads(registry_path.read_text(encoding="utf-8"))}
    records=[]
    for source_dir in sorted((ROOT/"data/raw").iterdir()):
        files=[]
        for p in sorted(source_dir.rglob("*")):
            if not p.is_file(): continue
            base={"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
            if p.suffix.lower()==".zip":
                with zipfile.ZipFile(p) as z:
                    for m in z.namelist():
                        item={**base,"archive_member":m}
                        if Path(m).suffix.lower() in (".csv",".xlsx",".xls"):
                            try:item.update(frame_profile(read_file(p,m)))
                            except Exception as e:item["profile_error"]=str(e)
                        files.append(item)
            else:
                try:
                    df=read_file(p)
                    if df is not None: base.update(frame_profile(df))
                except Exception as e: base["profile_error"]=str(e)
                files.append(base)
        meta=registry.get(source_dir.name,{})
        records.append({"source_name":source_dir.name,"source_url":URLS.get(source_dir.name) or meta.get("url"),"status":"profiled" if files else "not_downloaded","provenance":meta.get("provenance","unknown"),"license":meta.get("license","not identified"),"redistribution":meta.get("redistribution","unknown; verify upstream terms"),"intended_use":meta.get("intended_use","not yet assigned"),"approximate_grain":"must be confirmed per file from columns and source documentation","limitations":"Profiles are bounded samples; semantic keys require source-specific review.","files":files})
    out=ROOT/"data/metadata/data_sources.json"; out.write_text(json.dumps(records,indent=2),encoding="utf-8")
    lines=["# Data source inventory","","Generated from immutable local artifacts. Profiles are bounded to 250,000 rows per tabular file; hashes cover full files.",""]
    for r in records:
        lines += [f"## {r['source_name']}","",f"- Status: `{r['status']}`",f"- URL: {r['source_url'] or 'not registered'}",f"- Provenance: {r['provenance']}",f"- License: {r['license']}",f"- Redistribution: {r['redistribution']}",f"- Intended use: {r['intended_use']}",f"- Grain: {r['approximate_grain']}",f"- Limitations: {r['limitations']}",f"- Files: {len(r['files'])}",""]
        for f in r["files"]:
            lines += [f"### `{f.get('archive_member',f['path'])}`","",f"Size: {f['bytes']} bytes. Profiled rows: {f.get('profiled_rows','n/a')}. Duplicates in profile: {f.get('duplicate_rows','n/a')}.",""]
            if f.get("columns"):
                lines += ["| Column | Type | Null % | Unique |","|---|---:|---:|---:|"]+[f"| {c['name']} | {c['dtype']} | {c['null_pct']} | {c['unique']} |" for c in f["columns"]]+[""]
    (ROOT/"docs/data_sources.md").write_text("\n".join(lines),encoding="utf-8")
if __name__=="__main__": main()
