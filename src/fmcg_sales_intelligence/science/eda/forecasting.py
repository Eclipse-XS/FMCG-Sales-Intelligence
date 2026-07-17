from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from datetime import timedelta

from .common import load, numeric_summary, query, save_json, save_report, savefig


def run() -> dict:
    f = load("forecasting")
    sales = query("select * from analytics.fact_sales")
    total = f.height
    observed = sales.height
    missing = total - observed
    coverage = observed / total
    complete = f.filter(pl.col("target_observed_next_7d"))
    target = complete["target_units_next_7d"].cast(pl.Float64)
    target_stats = numeric_summary(complete, ["target_units_next_7d"])["target_units_next_7d"]
    target_stats["zero_count"] = int((target == 0).sum())
    target_stats["skewness"] = float(((target - target.mean()) ** 3).mean() / (target.std() ** 3))

    by_date = query("""with grid as (select sale_date,count(*) observed from analytics.fact_sales group by 1)
      select d.prediction_date,coalesce(g.observed,0) observed,960-coalesce(g.observed,0) missing,
      sum(case when f.target_observed_next_7d then 1 else 0 end) complete_targets
      from (select distinct prediction_date from read_parquet('data/processed/forecasting/forecasting_v1.parquet')) d
      left join grid g on g.sale_date=d.prediction_date
      join read_parquet('data/processed/forecasting/forecasting_v1.parquet') f using(prediction_date)
      group by 1,2 order by 1""")
    by_store = query("select store_id,count(*) observed, count(*)/4320.0 coverage from analytics.fact_sales group by 1 order by 1")
    by_sku = query("select sku_id,brand_name,category_name,count(*) observed,count(*)/1800.0 coverage from analytics.fact_sales group by all order by sku_id")
    by_brand = query("select brand_name,count(*) observed,count(*)/(count(distinct sku_id)*20*90.0) coverage from analytics.fact_sales group by 1 order by 1")
    by_category = query("select category_name,count(*) observed,count(*)/(count(distinct sku_id)*20*90.0) coverage from analytics.fact_sales group by 1 order by 1")
    by_series = query("""select store_id,sku_id,count(*) observed_days,count(*)/90.0 active_fraction
      from analytics.fact_sales group by 1,2 order by active_fraction""")
    gaps = query("""with x as (select store_id,sku_id,sale_date,lag(sale_date) over(partition by store_id,sku_id order by sale_date) prev from analytics.fact_sales)
      select date_diff('day',prev,sale_date) gap_days from x where prev is not null""")
    weekday = query("select dayname(sale_date) weekday,sum(quantity_units) units,count(*) positive_rows from analytics.fact_sales group by 1 order by 1")
    target_cutoff = f["prediction_date"].max() - timedelta(days=7)
    end_incomplete = f.filter(pl.col("prediction_date") > target_cutoff).height
    sparse_incomplete = f.filter((~pl.col("target_observed_next_7d")) & (pl.col("prediction_date") <= target_cutoff)).height

    numerical = ["lag_1", "lag_7", "lag_14", "lag_28", "rolling_mean_7d", "rolling_std_7d", "sales_velocity_7d", "scheduled_selling_price"]
    feature_missing = {c: int(f[c].null_count()) for c in numerical}
    correlations = {}
    for c in numerical:
        pair = complete.select(c, "target_units_next_7d").drop_nulls().cast({c: pl.Float64, "target_units_next_7d": pl.Float64})
        correlations[c] = float(np.corrcoef(pair[c], pair["target_units_next_7d"])[0, 1]) if pair.height > 2 and pair[c].std() else None
    target_groups = {
        "store": complete.group_by("store_id").agg(pl.len().alias("complete_rows"), pl.col("target_units_next_7d").mean().alias("mean_target")).sort("store_id").to_dicts(),
        "sku": complete.group_by("sku_id").agg(pl.len().alias("complete_rows"), pl.col("target_units_next_7d").mean().alias("mean_target")).sort("sku_id").to_dicts(),
        "brand": complete.group_by("brand_name").agg(pl.len().alias("complete_rows"), pl.col("target_units_next_7d").mean().alias("mean_target")).sort("brand_name").to_dicts(),
        "category": complete.group_by("category_name").agg(pl.len().alias("complete_rows"), pl.col("target_units_next_7d").mean().alias("mean_target")).sort("category_name").to_dicts(),
        "store_type": complete.group_by("store_type").agg(pl.len().alias("complete_rows"), pl.col("target_units_next_7d").mean().alias("mean_target")).sort("store_type").to_dicts(),
        "channel": complete.group_by("channel").agg(pl.len().alias("complete_rows"), pl.col("target_units_next_7d").mean().alias("mean_target")).sort("channel").to_dicts(),
        "date": complete.group_by("prediction_date").agg(pl.len().alias("complete_rows"), pl.col("target_units_next_7d").mean().alias("mean_target")).sort("prediction_date").to_dicts(),
    }

    plt.figure(figsize=(10, 4.8))
    x = by_date["prediction_date"].to_list()
    plt.plot(x, by_date["observed"], label="Observed positive-sale rows", color="#31688e")
    plt.plot(x, by_date["complete_targets"], label="Complete 7-day targets", color="#b73779")
    plt.xlabel("Date"); plt.ylabel("Store × SKU rows"); plt.title("Daily sales-row and target coverage"); plt.legend()
    coverage_fig = savefig("forecasting", "daily_coverage.png")

    plt.figure(figsize=(8, 4.8))
    plt.hist(target.to_numpy(), bins=25, color="#35b779", edgecolor="white")
    plt.xlabel("Observed units in (t, t+7]"); plt.ylabel("Complete target rows"); plt.title("Complete seven-day target distribution")
    target_fig = savefig("forecasting", "target_distribution.png")

    daily_sales = sales.group_by("sale_date").agg(pl.col("quantity_units").sum()).sort("sale_date")
    plt.figure(figsize=(10, 4.8)); plt.plot(daily_sales["sale_date"], daily_sales["quantity_units"], color="#31688e")
    plt.xlabel("Date"); plt.ylabel("Units sold"); plt.title("Aggregate observed daily sales")
    sales_fig = savefig("forecasting", "aggregate_daily_sales.png")

    metrics = {
        "prediction_rows": total, "observed_positive_sales_rows": observed, "observed_fraction": coverage,
        "missing_or_zero_sales_combinations": missing, "missing_fraction": missing / total,
        "complete_target_rows": complete.height, "complete_target_fraction": complete.height / total,
        "incomplete_due_dataset_end_rows": end_incomplete, "incomplete_due_sparse_sales_rows": sparse_incomplete,
        "target": target_stats, "feature_null_counts": feature_missing, "target_correlations": correlations,
        "series_active_fraction": numeric_summary(by_series, ["observed_days", "active_fraction"]),
        "inter_sale_gap_days": numeric_summary(gaps, ["gap_days"])["gap_days"],
        "coverage_by_date": by_date.to_dicts(), "coverage_by_store": by_store.to_dicts(), "coverage_by_sku": by_sku.to_dicts(),
        "coverage_by_brand": by_brand.to_dicts(), "coverage_by_category": by_category.to_dicts(),
        "target_by_group": target_groups, "weekday_sales": weekday.to_dicts(),
        "scheduled_promo_true_fraction": float(f["scheduled_is_promo"].mean()),
        "generator_semantics": "sales row emitted only when sold > 0; absence is observed zero sales, while latent demand can be censored by zero inventory",
    }
    save_json("forecasting", metrics)
    lines = ["# Forecasting EDA", "", "## Decision gate: meaning of an absent sales row", "", "**FACT:** `generate_dev_data.py` calculates `sold = min(latent, warehouse_stock)` and appends a sales record only inside `if sold:`. The generator evaluates every store × SKU × day. Therefore an absent row means observed sales were zero. It does not always mean latent demand was zero because stock constraints can censor demand.", "", "**CONCLUSION:** the frozen DE assumption ‘missing sales fact = unknown sales’ is wrong for this synthetic generator. For sales forecasting, absent rows should contribute zero. For latent-demand forecasting, stockout-censored cases require separate handling. No DE artifact was changed during EDA.", "", "## Coverage", "", f"- Prediction grid: {total:,}", f"- Positive-sale rows: {observed:,} ({coverage:.2%})", f"- Zero/absent sales combinations: {missing:,} ({missing/total:.2%})", f"- Fully observed current-contract targets: {complete.height:,} ({complete.height/total:.2%})", f"- Incomplete primarily from sparse positive-only facts: {sparse_incomplete:,}", f"- Rows affected by dataset-end seven-day truncation: {end_incomplete:,}", "", "The 1,035 complete targets are an artifact of requiring seven positive-sale rows, not a lack of calendar observation. This makes the current supervised artifact unsuitable for the intended experiment.", "", "## Target and series", "", f"- Complete-target mean: {target_stats['mean']:.2f}; median: {target_stats['median']:.2f}; p95: {target_stats['p95']:.2f}; max: {target_stats['max']:.2f}", f"- Complete-target zeros: {target_stats['zero_count']}", f"- Median active fraction per store–SKU: {metrics['series_active_fraction']['active_fraction']['median']:.2%}", f"- Median inter-sale gap: {metrics['inter_sale_gap_days']['median']:.1f} days; p95: {metrics['inter_sale_gap_days']['p95']:.1f} days", "", "All three promotion schedules cover every store and SKU for contiguous monthly periods, so `scheduled_is_promo` is constant true. It cannot identify promo-versus-non-promo differences. Price remains potentially useful because weekly price schedules vary.", "", "## Readiness", "", "**NOT READY.** The current target completeness rule is inconsistent with generator semantics and leaves only 1,035 supervised rows. The next DE decision must distinguish zero observed sales from inventory-censored latent demand and rebuild targets accordingly. Do not impute inside modeling as a workaround.", "", "Recommended later baselines after repair: seasonal naïve, moving average, Croston/TSB for intermittent series, and pooled count/regression baselines. Use chronological rolling-origin validation; never random splits.", "", f"![Coverage](../{coverage_fig})", "", f"![Target](../{target_fig})", "", f"![Daily sales](../{sales_fig})"]
    save_report("forecasting", lines)
    return metrics
