from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import csv
ROOT = PROJECT_ROOT
def read(name):
    with (ROOT/f"data/generated/{name}.csv").open(encoding="utf-8") as f:return list(csv.DictReader(f))
def main():
    checks=[]; sales=read("sales"); inv=read("inventory"); orders=read("orders"); items=read("order_items")
    def add(name,ok,detail):checks.append((name,ok,detail))
    keys=[(r["sale_date"],r["store_id"],r["sku_id"]) for r in sales]
    add("sales business key unique",len(keys)==len(set(keys)),f"rows={len(keys)}")
    add("sales nonnegative",all(float(r["quantity_units"])>=0 and float(r["net_revenue"])>=0 for r in sales),"")
    ik=[(r["snapshot_date"],r["warehouse_id"],r["sku_id"]) for r in inv]
    add("inventory business key unique",len(ik)==len(set(ik)),f"rows={len(ik)}")
    add("inventory nonnegative",all(int(r["stock_quantity"])>=0 for r in inv),"")
    ordered=sorted(inv,key=lambda r:(int(r["warehouse_id"]),int(r["sku_id"]),r["snapshot_date"]))
    prior={}; flow_ok=True
    for r in ordered:
        k=(r["warehouse_id"],r["sku_id"]); stock=int(r["stock_quantity"])
        if k in prior:
            expected=prior[k]-int(r["demand_fulfilled"])+int(r["replenishment_quantity"])+int(r["adjustment_quantity"])
            flow_ok &= stock==expected
        prior[k]=stock
    add("inventory flow equation",flow_ok,"stock[t] = stock[t-1] - fulfilled + replenishment + adjustment")
    order_ids={r["order_id"] for r in orders}; add("order items have parents",all(r["order_id"] in order_ids for r in items),f"items={len(items)}")
    totals={oid:0.0 for oid in order_ids}
    for r in items:totals[r["order_id"]]+=int(r["quantity"])*float(r["unit_price"])-float(r["discount_amount"])
    add("order totals reconcile",all(abs(totals[r["order_id"]]-float(r["total_amount"]))<0.011 for r in orders),"tolerance=0.01")
    text=["# Data quality report","","Generated validation results.","","| Check | Result | Detail |","|---|---|---|"]+[f"| {n} | {'PASS' if ok else 'FAIL'} | {d} |" for n,ok,d in checks]
    (ROOT/"artifacts/reports/data_quality_report.md").write_text("\n".join(text)+"\n",encoding="utf-8")
    if not all(x[1] for x in checks):raise SystemExit(1)
if __name__=="__main__":main()
