"""Emit reproducible diagnostics for Promotion Data Contract V1."""
from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT

import json

import duckdb


ROOT = PROJECT_ROOT
DB = ROOT / "data/warehouse/fmcg.duckdb"
OUT = ROOT / "artifacts/reports/data_refinement"


def scalar(connection: duckdb.DuckDBPyConnection, sql: str) -> int | float:
    return connection.execute(sql).fetchone()[0]


def main() -> None:
    daily = "analytics.mart_promotion_daily"
    exposure = "analytics.mart_promotion_performance"
    with duckdb.connect(str(DB), read_only=True) as connection:
        diagnostics = {
            "promotion_count": scalar(connection, f"select count(distinct promotion_id) from {daily}"),
            "store_count": scalar(connection, f"select count(distinct store_id) from {daily}"),
            "sku_count": scalar(connection, f"select count(distinct sku_id) from {daily}"),
            "exposure_count": scalar(connection, f"select count(*) from {exposure}"),
            "duplicate_exposures": scalar(connection, f"select count(*) from (select promotion_id,store_id,sku_id from {exposure} group by all having count(*)>1)"),
            "daily_grid_rows": scalar(connection, f"select count(*) from {daily}"),
            "duplicate_daily_keys": scalar(connection, f"select count(*) from (select promotion_id,store_id,sku_id,calendar_date from {daily} group by all having count(*)>1)"),
            "observable_daily_rows": scalar(connection, f"select count(*) from {daily} where is_observable"),
            "boundary_unobservable_rows": scalar(connection, f"select count(*) from {daily} where not is_observable"),
            "observed_zero_sales_rows": scalar(connection, f"select count(*) from {daily} where is_observable and realized_sales_units=0"),
            "positive_sales_rows": scalar(connection, f"select count(*) from {daily} where is_observable and realized_sales_units>0"),
            "observable_price_null_rows": scalar(connection, f"select count(*) from {daily} where is_observable and valid_selling_price is null"),
            "overlap_exposure_days": scalar(connection, f"select count(*) from {daily} where promotion_overlap"),
            "overlap_exposures": scalar(connection, f"select count(*) from {exposure} where promotion_overlap"),
            "pre_complete_exposures": scalar(connection, f"select count(*) from {exposure} where pre_window_complete"),
            "during_complete_exposures": scalar(connection, f"select count(*) from {exposure} where during_window_complete"),
            "post_complete_exposures": scalar(connection, f"select count(*) from {exposure} where post_window_complete"),
            "pre_vs_during_eligible": scalar(connection, f"select count(*) from {exposure} where eligible_pre_vs_during"),
            "during_vs_post_eligible": scalar(connection, f"select count(*) from {exposure} where eligible_during_vs_post"),
            "full_cycle_eligible": scalar(connection, f"select count(*) from {exposure} where eligible_full_cycle"),
            "complete_zero_sales_windows": scalar(connection, f"select count(*) from {exposure} where (pre_window_complete and pre_realized_units=0) or (during_window_complete and during_realized_units=0) or (post_window_complete and post_realized_units=0)"),
            "daily_grid_realized_units": scalar(connection, f"select sum(realized_sales_units) from {daily} where is_observable"),
            "authoritative_realized_units": scalar(connection, f"select sum(d.realized_sales_units) from {daily} p join analytics.fact_daily_demand d on d.observation_date=p.calendar_date and d.store_id=p.store_id and d.sku_id=p.sku_id where p.is_observable"),
        }
    diagnostics["reconciliation_difference"] = diagnostics["daily_grid_realized_units"] - diagnostics["authoritative_realized_units"]
    diagnostics["inventory_context_available"] = True
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "promotion_contract_v1.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    lines = ["# Promotion Data Contract V1 diagnostics", ""] + [f"- {key}: {value}" for key, value in diagnostics.items()]
    (OUT / "promotion_contract_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
