"""Idempotently replicate the operational PostgreSQL schema into local DuckDB raw tables."""
from __future__ import annotations
import json, logging
from datetime import datetime, timezone
from pathlib import Path
import duckdb, polars as pl
from psycopg import sql
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "database"))
from connection import connect

ROOT=Path(__file__).resolve().parents[2]; WAREHOUSE=ROOT/"data/warehouse"; DB=WAREHOUSE/"fmcg.duckdb"
TABLES=["categories","brands","products","skus","regions","stores","warehouses","promotions","promotion_skus","promotion_stores","product_prices","sales","daily_demand","orders","order_items","deliveries","delivery_items","inventory"]
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s"); log=logging.getLogger(__name__)
def main():
    WAREHOUSE.mkdir(parents=True,exist_ok=True); metadata={"built_at":datetime.now(timezone.utc).isoformat(),"source":"postgresql:fmcg","tables":{}}
    with connect() as pg, duckdb.connect(str(DB)) as dwh:
        for table in TABLES:
            with pg.cursor() as cur:
                cur.execute(sql.SQL("SELECT * FROM fmcg.{} ORDER BY 1").format(sql.Identifier(table)))
                rows=cur.fetchall(); cols=[x.name for x in cur.description]
            frame=pl.DataFrame(rows,schema=cols,orient="row",infer_schema_length=None); dwh.register("_frame",frame.to_arrow())
            dwh.execute(f"CREATE SCHEMA IF NOT EXISTS raw; CREATE OR REPLACE TABLE raw.{table} AS SELECT * FROM _frame")
            parquet=WAREHOUSE/"raw"/f"{table}.parquet"; parquet.parent.mkdir(exist_ok=True); frame.write_parquet(parquet)
            metadata["tables"][table]={"row_count":frame.height,"columns":frame.columns,"parquet":str(parquet.relative_to(ROOT))};log.info("replicated %s: %s rows",table,frame.height)
    (WAREHOUSE/"replication_metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
if __name__=="__main__":main()
