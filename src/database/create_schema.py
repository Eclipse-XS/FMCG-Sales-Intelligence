from __future__ import annotations
import argparse
from pathlib import Path
from connection import connect
ROOT=Path(__file__).resolve().parents[2]
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--reset",action="store_true",help="Drop only the fmcg schema before recreation");args=ap.parse_args()
    with connect() as conn:
        with conn.cursor() as cur:
            if args.reset:cur.execute("DROP SCHEMA IF EXISTS fmcg CASCADE")
            cur.execute((ROOT/"db/schema.sql").read_text(encoding="utf-8"))
    print("fmcg schema created" + (" from a clean reset" if args.reset else ""))
if __name__=="__main__":main()

