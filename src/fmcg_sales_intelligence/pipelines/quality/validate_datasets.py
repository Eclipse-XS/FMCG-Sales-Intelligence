"""Great Expectations validations focused on output data contracts, not duplicate OLTP constraints."""
from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import json
from datetime import datetime,timezone
import great_expectations as gx
from great_expectations.expectations import ExpectColumnToExist,ExpectColumnValuesToNotBeNull,ExpectColumnValuesToBeBetween,ExpectCompoundColumnsToBeUnique
import polars as pl

ROOT = PROJECT_ROOT; BASE=ROOT/"data/processed"; REPORT=ROOT/"artifacts/reports/data_engineering"
SPECS={
 "forecasting":("forecasting/forecasting_v1.parquet",["prediction_date","store_id","sku_id"],["scheduled_selling_price","target_units_next_7d","target_requested_demand_next_7d","target_lost_sales_next_7d"]),
 "stockout":("stockout/stockout_v1.parquet",["prediction_date","warehouse_id","sku_id"],["available_quantity","stock_quantity"]),
 "segmentation":("segmentation/segmentation_v1.parquet",["snapshot_date","store_id"],["revenue_30d","units_30d"]),
 "segment_assignment":("segment_assignment/segment_assignment_v1.parquet",["snapshot_date","store_id"],["revenue_30d","units_30d"]),
 "anomaly":("anomaly/anomaly_v1.parquet",["event_date","store_id","sku_id"],["event_observed_units","event_transaction_unit_price"]),
 "basket":("basket/basket_v1.parquet",["order_id","sku_id"],["quantity"]),
 "promotion_daily":("promotion_daily/promotion_daily_v1.parquet",["promotion_id","store_id","sku_id","calendar_date"],["promotion_duration_days"]),
 "promotion_performance":("promotion_performance/promotion_performance_v1.parquet",["promotion_id","store_id","sku_id"],[]),
}
def main():
    context=gx.get_context(mode="ephemeral"); ds=context.data_sources.add_pandas(name="datasets"); results={"ran_at":datetime.now(timezone.utc).isoformat(),"engine":"Great Expectations","datasets":{}}; passed=True
    for name,(relative,keys,nonnegative) in SPECS.items():
        frame=pl.read_parquet(BASE/relative).to_pandas(); asset=ds.add_dataframe_asset(name=name); definition=asset.add_batch_definition_whole_dataframe(name="runtime"); batch=asset.get_batch(definition.build_batch_request({"dataframe":frame}))
        expectations=[ExpectColumnToExist(column=c) for c in keys+nonnegative]+[ExpectColumnValuesToNotBeNull(column=c) for c in keys]+[ExpectCompoundColumnsToBeUnique(column_list=keys)]+[ExpectColumnValuesToBeBetween(column=c,min_value=0) for c in nonnegative]
        validations=[]
        for expectation in expectations:
            result=batch.validate(expectation); validations.append({"expectation":expectation.expectation_type,"success":bool(result.success)})
        ok=all(x["success"] for x in validations);passed &= ok;results["datasets"][name]={"rows":len(frame),"expectations":validations,"passed":ok}
    results["passed"]=passed;REPORT.mkdir(parents=True,exist_ok=True);(REPORT/"great_expectations_validation.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    lines=["# Great Expectations dataset validation","",f"Overall: **{'PASS' if passed else 'FAIL'}**.",""]
    for name,r in results["datasets"].items():lines += [f"## {name}","",f"Rows: {r['rows']}; expectations: {len(r['expectations'])}; result: **{'PASS' if r['passed'] else 'FAIL'}**.",""]
    (REPORT/"great_expectations_validation.md").write_text("\n".join(lines),encoding="utf-8")
    if not passed:raise SystemExit(1)
if __name__=="__main__":main()
