from pathlib import Path
import json

import duckdb
import polars as pl

ROOT = Path(__file__).resolve().parents[2]


def test_generator_preserves_complete_demand_but_sales_remain_positive_only():
    source = (ROOT / "src/fmcg_sales_intelligence/pipelines/generation/generate_dev_data.py").read_text(encoding="utf-8")
    assert "sold=min(latent,available_before)" in source
    assert 'write("daily_demand"' in source
    assert "if sold:" in source


def test_forecast_coverage_decomposition():
    f = pl.read_parquet(ROOT / "data/processed/forecasting/forecasting_v1.parquet")
    with duckdb.connect(str(ROOT / "data/warehouse/fmcg.duckdb"), read_only=True) as conn:
        observed = conn.execute("select count(*) from analytics.fact_sales").fetchone()[0]
        positive = conn.execute("select count(*) from analytics.fact_daily_demand where realized_sales_units > 0").fetchone()[0]
    assert f.height == 90 * 20 * 48
    assert observed == positive
    assert f.filter(pl.col("target_observed_next_7d")).height == (90 - 7) * 20 * 48
    assert f.filter(pl.col("target_observed_next_7d") & pl.col("target_units_next_7d").is_null()).height == 0


def test_stockout_eda_target_counts_are_exhaustive():
    f = pl.read_parquet(ROOT / "data/processed/stockout/stockout_v1.parquet")
    event = f.filter(pl.col("event_observed")).height
    complete_nonevent = f.filter((~pl.col("event_observed")) & pl.col("horizon_complete")).height
    incomplete_nonevent = f.filter((~pl.col("event_observed")) & (~pl.col("horizon_complete"))).height
    assert event + complete_nonevent + incomplete_nonevent == f.height
    assert event > 14
    assert f.filter(~pl.col("horizon_complete")).height == 7 * 4 * 48


def test_basket_descriptive_counts():
    f = pl.read_parquet(ROOT / "data/processed/basket/basket_v1.parquet")
    assert f["order_id"].n_unique() == 2000
    assert f["sku_id"].n_unique() == 48
    assert f.select(["order_id", "sku_id"]).is_duplicated().sum() == 0


def test_eda_manifest_and_all_section_metrics_exist():
    manifest = json.loads((ROOT / "artifacts/reports/eda/run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "PASS"
    for section in manifest["sections"]:
        assert (ROOT / f"artifacts/reports/eda/{section}/metrics.json").exists()
