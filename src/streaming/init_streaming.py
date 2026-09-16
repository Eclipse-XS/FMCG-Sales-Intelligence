from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"database"))
from connection import connect
def main():
    with connect() as conn,conn.cursor() as cur:
        cur.execute("""CREATE SCHEMA IF NOT EXISTS streaming;
        CREATE TABLE IF NOT EXISTS streaming.event_ledger(event_id uuid PRIMARY KEY,event_type text NOT NULL,event_time timestamptz NOT NULL,ingestion_time timestamptz NOT NULL DEFAULT now(),source text NOT NULL,schema_version integer NOT NULL,payload jsonb NOT NULL,status text NOT NULL CHECK(status IN ('accepted','rejected')));
        CREATE TABLE IF NOT EXISTS streaming.sales_replay(event_id uuid PRIMARY KEY,sale_id bigint NOT NULL,store_id bigint NOT NULL,sku_id bigint NOT NULL,event_time timestamptz NOT NULL,quantity_units integer NOT NULL CHECK(quantity_units>=0),unit_price numeric(12,2) NOT NULL CHECK(unit_price>=0),payload jsonb NOT NULL);
        CREATE TABLE IF NOT EXISTS streaming.dead_letters(event_id uuid PRIMARY KEY,event_time timestamptz,reason text NOT NULL,raw_event jsonb,received_at timestamptz NOT NULL DEFAULT now());""")
    print("streaming schema initialized")
if __name__=="__main__":main()

