from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import argparse
from fmcg_sales_intelligence.pipelines.persistence.connection import connect
ROOT = PROJECT_ROOT
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--reset",action="store_true",help="Drop only the fmcg schema before recreation");args=ap.parse_args()
    with connect() as conn:
        with conn.cursor() as cur:
            if args.reset:cur.execute("DROP SCHEMA IF EXISTS fmcg CASCADE")
            cur.execute((ROOT/"platform/postgres/schema.sql").read_text(encoding="utf-8"))
    print("fmcg schema created" + (" from a clean reset" if args.reset else ""))
if __name__=="__main__":main()

