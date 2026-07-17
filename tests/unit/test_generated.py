import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def rows(name):
    with (ROOT/f"data/generated/{name}.csv").open(encoding="utf-8") as f:return list(csv.DictReader(f))
def test_sales_business_key_and_values():
    data=rows("sales"); keys={(r["sale_date"],r["store_id"],r["sku_id"]) for r in data}
    assert len(keys)==len(data)
    assert all(int(r["quantity_units"])>=0 and float(r["net_revenue"])>=0 for r in data)
def test_inventory_nonnegative_and_unique():
    data=rows("inventory"); keys={(r["snapshot_date"],r["warehouse_id"],r["sku_id"]) for r in data}
    assert len(keys)==len(data)
    assert all(int(r["stock_quantity"])>=0 for r in data)

def test_daily_demand_complete_and_reconciled():
    data=rows("daily_demand"); keys={(r["observation_date"],r["store_id"],r["sku_id"]) for r in data}
    assert len(keys)==len(data)==90*20*48
    assert all(int(r["requested_demand_units"])==int(r["realized_sales_units"])+int(r["lost_sales_units"]) for r in data)
    assert all((r["demand_censored_by_inventory"]=="True")== (int(r["lost_sales_units"])>0) for r in data)

def test_inventory_daily_conservation():
    for r in rows("inventory"):
        assert int(r["stock_quantity"])==int(r["opening_stock_quantity"])+int(r["replenishment_quantity"])-int(r["demand_fulfilled"])+int(r["adjustment_quantity"])
        assert int(r["demand_requested"])==int(r["demand_fulfilled"])+int(r["lost_sales_quantity"])
