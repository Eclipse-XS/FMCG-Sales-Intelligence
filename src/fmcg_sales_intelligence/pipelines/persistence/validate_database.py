from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import json,re
import psycopg
from fmcg_sales_intelligence.pipelines.persistence.connection import connect
ROOT = PROJECT_ROOT;DATA=ROOT/"data/generated"
TABLES=["categories","brands","products","skus","regions","stores","warehouses","promotions","promotion_skus","promotion_stores","product_prices","sales","daily_demand","orders","order_items","deliveries","delivery_items","inventory"]
def csv_count(table):
    with (DATA/f"{table}.csv").open(encoding="utf-8") as f:return sum(1 for _ in f)-1
CHECKS={
"orphan sales sku":"SELECT count(*) FROM fmcg.sales x LEFT JOIN fmcg.skus p USING(sku_id) WHERE p.sku_id IS NULL",
"orphan sales store":"SELECT count(*) FROM fmcg.sales x LEFT JOIN fmcg.stores p USING(store_id) WHERE p.store_id IS NULL",
"orphan daily demand":"SELECT count(*) FROM fmcg.daily_demand x LEFT JOIN fmcg.stores s USING(store_id) LEFT JOIN fmcg.skus k USING(sku_id) LEFT JOIN fmcg.warehouses w USING(warehouse_id) WHERE s.store_id IS NULL OR k.sku_id IS NULL OR w.warehouse_id IS NULL",
"orphan inventory sku":"SELECT count(*) FROM fmcg.inventory x LEFT JOIN fmcg.skus p USING(sku_id) WHERE p.sku_id IS NULL",
"orphan inventory warehouse":"SELECT count(*) FROM fmcg.inventory x LEFT JOIN fmcg.warehouses p USING(warehouse_id) WHERE p.warehouse_id IS NULL",
"orphan order items order":"SELECT count(*) FROM fmcg.order_items x LEFT JOIN fmcg.orders p USING(order_id) WHERE p.order_id IS NULL",
"orphan order items sku":"SELECT count(*) FROM fmcg.order_items x LEFT JOIN fmcg.skus p USING(sku_id) WHERE p.sku_id IS NULL",
"orphan promotion sku mapping":"SELECT count(*) FROM fmcg.promotion_skus x LEFT JOIN fmcg.promotions p USING(promotion_id) LEFT JOIN fmcg.skus s USING(sku_id) WHERE p.promotion_id IS NULL OR s.sku_id IS NULL",
"orphan promotion store mapping":"SELECT count(*) FROM fmcg.promotion_stores x LEFT JOIN fmcg.promotions p USING(promotion_id) LEFT JOIN fmcg.stores s USING(store_id) WHERE p.promotion_id IS NULL OR s.store_id IS NULL",
"orphan price":"SELECT count(*) FROM fmcg.product_prices x LEFT JOIN fmcg.skus k USING(sku_id) LEFT JOIN fmcg.stores s USING(store_id) WHERE k.sku_id IS NULL OR s.store_id IS NULL",
"duplicate sales grain":"SELECT count(*) FROM (SELECT sale_date,store_id,sku_id FROM fmcg.sales GROUP BY 1,2,3 HAVING count(*)>1)x",
"duplicate demand grain":"SELECT count(*) FROM (SELECT observation_date,store_id,sku_id FROM fmcg.daily_demand GROUP BY 1,2,3 HAVING count(*)>1)x",
"duplicate inventory grain":"SELECT count(*) FROM (SELECT snapshot_date,warehouse_id,sku_id FROM fmcg.inventory GROUP BY 1,2,3 HAVING count(*)>1)x",
"duplicate price start grain":"SELECT count(*) FROM (SELECT valid_from,store_id,sku_id FROM fmcg.product_prices GROUP BY 1,2,3 HAVING count(*)>1)x",
"overlapping price periods":"SELECT count(*) FROM fmcg.product_prices a JOIN fmcg.product_prices b ON a.store_id=b.store_id AND a.sku_id=b.sku_id AND a.price_id<b.price_id AND daterange(a.valid_from,a.valid_to,'[]') && daterange(b.valid_from,b.valid_to,'[]')",
"invalid sales numerics":"SELECT count(*) FROM fmcg.sales WHERE quantity_units<0 OR unit_price<0 OR gross_revenue<0 OR discount_amount<0 OR discount_amount>gross_revenue OR net_revenue<>gross_revenue-discount_amount OR gross_profit<>net_revenue-quantity_units*unit_cost",
"invalid inventory numerics":"SELECT count(*) FROM fmcg.inventory WHERE stock_quantity<0 OR reserved_quantity<0 OR available_quantity<0",
"invalid demand reconciliation":"SELECT count(*) FROM fmcg.daily_demand WHERE requested_demand_units<>realized_sales_units+lost_sales_units OR demand_censored_by_inventory<>(lost_sales_units>0)",
"order reconciliation":"SELECT count(*) FROM (SELECT o.order_id,o.total_amount,COALESCE(sum(oi.line_total),0) lines FROM fmcg.orders o LEFT JOIN fmcg.order_items oi USING(order_id) GROUP BY o.order_id)x WHERE abs(total_amount-lines)>0.01",
"inventory flow":"WITH x AS (SELECT *,lag(stock_quantity) OVER(PARTITION BY warehouse_id,sku_id ORDER BY snapshot_date) prev FROM fmcg.inventory) SELECT count(*) FROM x WHERE prev IS NOT NULL AND stock_quantity<>prev+replenishment_quantity-demand_fulfilled+adjustment_quantity",
"daily demand to inventory reconciliation":"SELECT count(*) FROM fmcg.inventory i LEFT JOIN (SELECT observation_date,warehouse_id,sku_id,sum(requested_demand_units) requested,sum(realized_sales_units) realized,sum(lost_sales_units) lost FROM fmcg.daily_demand GROUP BY 1,2,3) d ON d.observation_date=i.snapshot_date AND d.warehouse_id=i.warehouse_id AND d.sku_id=i.sku_id WHERE i.demand_requested<>d.requested OR i.demand_fulfilled<>d.realized OR i.lost_sales_quantity<>d.lost",
"invalid promotion dates":"SELECT count(*) FROM fmcg.promotions WHERE end_date<start_date",
"invalid price dates":"SELECT count(*) FROM fmcg.product_prices WHERE valid_to<valid_from",
"invalid order chronology":"SELECT count(*) FROM fmcg.orders WHERE requested_delivery_date<order_date OR actual_delivery_date<order_date",
"invalid delivery chronology":"SELECT count(*) FROM fmcg.deliveries WHERE delivered_at<shipped_at",
"unmapped promoted sale":"SELECT count(*) FROM fmcg.sales s WHERE promotion_id IS NOT NULL AND (NOT EXISTS(SELECT 1 FROM fmcg.promotion_skus p WHERE p.promotion_id=s.promotion_id AND p.sku_id=s.sku_id) OR NOT EXISTS(SELECT 1 FROM fmcg.promotion_stores p WHERE p.promotion_id=s.promotion_id AND p.store_id=s.store_id))"
}
INVALID={
"orphan order item":"INSERT INTO fmcg.order_items(order_id,sku_id,quantity,unit_price,discount_amount) VALUES(999999999,1,1,1,0)",
"orphan sale":"INSERT INTO fmcg.sales(sale_date,store_id,sku_id,quantity_units,unit_price,gross_revenue,discount_amount,net_revenue,unit_cost,gross_profit) VALUES('2030-01-01',999999999,1,1,1,1,0,1,.5,.5)",
"negative quantity":"INSERT INTO fmcg.order_items(order_id,sku_id,quantity,unit_price,discount_amount) VALUES(1,1,-1,1,0)",
"duplicate sales grain":"INSERT INTO fmcg.sales(sale_date,store_id,sku_id,quantity_units,unit_price,gross_revenue,discount_amount,net_revenue,unit_cost,gross_profit) SELECT sale_date,store_id,sku_id,quantity_units,unit_price,gross_revenue,discount_amount,net_revenue,unit_cost,gross_profit FROM fmcg.sales LIMIT 1",
"duplicate inventory grain":"INSERT INTO fmcg.inventory(snapshot_date,warehouse_id,sku_id,stock_quantity,reserved_quantity,reorder_point,safety_stock) SELECT snapshot_date,warehouse_id,sku_id,stock_quantity,reserved_quantity,reorder_point,safety_stock FROM fmcg.inventory LIMIT 1",
"invalid promotion range":"INSERT INTO fmcg.promotions(promotion_name,promotion_type,start_date,end_date,discount_type,discount_value) VALUES('bad','test','2030-02-01','2030-01-01','percentage',10)",
"invalid price":"INSERT INTO fmcg.product_prices(store_id,sku_id,valid_from,valid_to,regular_price,selling_price) VALUES(1,1,'2030-01-01','2030-01-07',1,2)"
}
def main():
    report={"row_counts":{},"checks":{},"constraint_tests":{},"smoke_queries":[]}
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SHOW server_version");report["postgresql_version"]=cur.fetchone()[0]
            cur.execute("SELECT current_database() ");report["database"]=cur.fetchone()[0]
            for table in TABLES:
                cur.execute(f"SELECT count(*) FROM fmcg.{table}");actual=cur.fetchone()[0];expected=csv_count(table)
                report["row_counts"][table]={"database":actual,"csv":expected,"match":actual==expected}
            for name,query in CHECKS.items():
                cur.execute(query);value=cur.fetchone()[0];report["checks"][name]={"violations":value,"pass":value==0}
            for i,(name,statement) in enumerate(INVALID.items()):
                sp=f"invalid_{i}";cur.execute(f"SAVEPOINT {sp}")
                try:cur.execute(statement);rejected=False
                except psycopg.Error:cur.execute(f"ROLLBACK TO SAVEPOINT {sp}");rejected=True
                cur.execute(f"RELEASE SAVEPOINT {sp}");report["constraint_tests"][name]={"rejected":rejected}
            sql_text=(ROOT/"platform/postgres/queries/smoke.sql").read_text(encoding="utf-8")
            for number,statement in enumerate([x.strip() for x in re.split(r";\s*(?:\n|$)",sql_text) if x.strip()],1):
                cur.execute(statement);rows=cur.fetchmany(5);report["smoke_queries"].append({"query":number,"executed":True,"sample_rows":len(rows)})
        conn.rollback()
    passed=all(x["match"] for x in report["row_counts"].values()) and all(x["pass"] for x in report["checks"].values()) and all(x["rejected"] for x in report["constraint_tests"].values()) and all(x["executed"] for x in report["smoke_queries"])
    report["passed"]=passed;(ROOT/"artifacts/reports/database_validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    lines=["# Operational database validation","",f"Database: `{report['database']}`; PostgreSQL `{report['postgresql_version']}`; overall: **{'PASS' if passed else 'FAIL'}**.","","## Row counts","","| Table | CSV | Database | Match |","|---|---:|---:|---|"]+[f"| {t} | {x['csv']} | {x['database']} | {x['match']} |" for t,x in report["row_counts"].items()]+["","## Integrity and business rules","","| Check | Violations | Result |","|---|---:|---|"]+[f"| {n} | {x['violations']} | {'PASS' if x['pass'] else 'FAIL'} |" for n,x in report["checks"].items()]+["","## Deliberate invalid inserts","","| Case | Rejected |","|---|---|"]+[f"| {n} | {x['rejected']} |" for n,x in report["constraint_tests"].items()]+["",f"Smoke queries executed: {len(report['smoke_queries'])}/{len(report['smoke_queries'])}."]
    (ROOT/"artifacts/reports/database_validation.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
