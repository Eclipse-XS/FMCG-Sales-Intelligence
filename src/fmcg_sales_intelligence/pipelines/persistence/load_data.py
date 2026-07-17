from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import csv
from psycopg import sql
from fmcg_sales_intelligence.pipelines.persistence.connection import connect
ROOT = PROJECT_ROOT;DATA=ROOT/"data/generated"
LOAD_ORDER=["categories","brands","regions","products","skus","stores","warehouses","promotions","promotion_skus","promotion_stores","product_prices","sales","daily_demand","orders","order_items","deliveries","delivery_items","inventory"]
IDENTITY_TABLES={"categories":"category_id","brands":"brand_id","regions":"region_id","products":"product_id","skus":"sku_id","stores":"store_id","warehouses":"warehouse_id","promotions":"promotion_id","product_prices":"price_id","sales":"sale_id","daily_demand":"demand_observation_id","orders":"order_id","order_items":"order_item_id","deliveries":"delivery_id","inventory":"inventory_id"}
def main():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO fmcg, public")
            for table in LOAD_ORDER:
                path=DATA/f"{table}.csv"
                if not path.exists():raise FileNotFoundError(f"Missing canonical input: {path}")
                with path.open(encoding="utf-8",newline="") as f:
                    columns=next(csv.reader(f));f.seek(0)
                    query=sql.SQL("COPY {} ({}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')").format(sql.Identifier(table),sql.SQL(',').join(map(sql.Identifier,columns)))
                    with cur.copy(query) as copy:
                        while block:=f.read(1024*1024):copy.write(block)
                cur.execute(sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table)));print(f"loaded {table}: {cur.fetchone()[0]}")
            for table,key in IDENTITY_TABLES.items():
                query=sql.SQL("SELECT setval(pg_get_serial_sequence(%s,%s), COALESCE(MAX({}),1), true) FROM {}").format(sql.Identifier(key),sql.Identifier(table))
                cur.execute(query,(f"fmcg.{table}",key))
            cur.execute((ROOT/"platform/postgres/indexes.sql").read_text(encoding="utf-8"))
    print("canonical dev data committed")
if __name__=="__main__":main()
