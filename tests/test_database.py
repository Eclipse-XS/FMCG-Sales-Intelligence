import csv,sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src/database"))
from connection import connect

TABLES=["categories","brands","regions","products","skus","stores","warehouses","promotions","promotion_skus","promotion_stores","product_prices","sales","daily_demand","orders","order_items","deliveries","delivery_items","inventory"]
def db():
    try:return connect()
    except Exception as exc:pytest.skip(f"PostgreSQL unavailable: {exc}")
def source_count(table):
    with (ROOT/f"data/generated/{table}.csv").open(encoding="utf-8") as f:return sum(1 for _ in f)-1
def test_database_counts_match_generated_sources():
    with db() as conn,conn.cursor() as cur:
        for table in TABLES:
            cur.execute(f"SELECT count(*) FROM fmcg.{table}")
            assert cur.fetchone()[0]==source_count(table),table
def test_business_grains_and_order_totals():
    queries=[
      "SELECT count(*) FROM (SELECT sale_date,store_id,sku_id FROM fmcg.sales GROUP BY 1,2,3 HAVING count(*)>1)x",
      "SELECT count(*) FROM (SELECT snapshot_date,warehouse_id,sku_id FROM fmcg.inventory GROUP BY 1,2,3 HAVING count(*)>1)x",
      "SELECT count(*) FROM (SELECT store_id,sku_id,valid_from FROM fmcg.product_prices GROUP BY 1,2,3 HAVING count(*)>1)x",
      "SELECT count(*) FROM (SELECT o.order_id,o.total_amount,sum(oi.line_total) lines FROM fmcg.orders o JOIN fmcg.order_items oi USING(order_id) GROUP BY o.order_id)x WHERE abs(total_amount-lines)>.01"
    ]
    with db() as conn,conn.cursor() as cur:
        for query in queries:cur.execute(query);assert cur.fetchone()[0]==0
def test_required_indexes_exist():
    with db() as conn,conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM pg_indexes WHERE schemaname='fmcg' AND indexname IN ('sales_sku_store_date_idx','inventory_warehouse_sku_date_idx','orders_store_date_idx','prices_lookup_idx')")
        assert cur.fetchone()[0]==4
