"""Download immutable upstream artifacts; never transforms data/raw in place."""
from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import argparse, json, shutil, urllib.request
from pathlib import Path

ROOT = PROJECT_ROOT
RAW = ROOT / "data" / "raw"
SOURCES = {
 "online_retail_ii": {"kind":"url", "url":"https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"},
 "favorita": {"kind":"competition", "handle":"favorita-grocery-sales-forecasting"},
 "m5": {"kind":"competition", "handle":"m5-forecasting-accuracy"},
 "instacart": {"kind":"competition", "handle":"instacart-market-basket-analysis"},
 "grocery_inventory": {"kind":"dataset", "handle":"salahuddinahmedshuvo/grocery-inventory-and-sales-dataset"},
 "supply_chain_inventory": {"kind":"dataset", "handle":"ziya07/high-dimensional-supply-chain-inventory-dataset"},
 "retail_warehouse": {"kind":"dataset", "handle":"datarspectrum/retail-data-warehouse-12-table-1m-rows-dataset"},
 "fmcg_daily": {"kind":"dataset", "handle":"beatafaron/fmcg-daily-sales-data-to-2022-2024"},
 "retail_fmcg_2024": {"kind":"dataset", "handle":"arannayavadebnath/retail-fmcg-sales-dataset-2024"},
}

def download_one(name: str) -> dict:
    spec, target = SOURCES[name], RAW / name
    target.mkdir(parents=True, exist_ok=True)
    try:
        if spec["kind"] == "url":
            out = target / Path(spec["url"]).name
            existing = next(target.glob("*.zip"), None)
            if existing is not None: out = existing
            if not out.exists(): urllib.request.urlretrieve(spec["url"], out)
            return {"source":name,"status":"downloaded","path":str(out.relative_to(ROOT))}
        import kagglehub
        if spec["kind"] == "competition":
            cached = Path(kagglehub.competition_download(spec["handle"]))
        else:
            cached = Path(kagglehub.dataset_download(spec["handle"]))
        for f in cached.rglob("*"):
            if f.is_file():
                dest = target / f.relative_to(cached); dest.parent.mkdir(parents=True,exist_ok=True)
                if not dest.exists(): shutil.copy2(f,dest)
        return {"source":name,"status":"downloaded","path":str(target.relative_to(ROOT))}
    except Exception as exc:
        status = "blocked_auth_or_terms" if any(x in str(exc).lower() for x in ("401","403","credential","authenticate","permission")) else "failed"
        return {"source":name,"status":status,"error":str(exc)[:500]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("sources",nargs="*",default=list(SOURCES)); args=ap.parse_args()
    results=[download_one(x) for x in args.sources]
    out=ROOT/"data/metadata/download_status.json"; out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps(results,indent=2))
    if any(x["status"]=="blocked_auth_or_terms" for x in results): raise SystemExit(2)
if __name__ == "__main__": main()
