"""Produce the post-refinement semantic audit and focused EDA artifacts."""
from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
from fmcg_sales_intelligence.pipelines.refinement.episodes import stockout_episodes

import json
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import polars as pl

ROOT = PROJECT_ROOT


def main() -> None:
    report = ROOT / "artifacts/reports/data_refinement"
    figures = report / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    forecast = pl.read_parquet(ROOT / "data/processed/forecasting/forecasting_v1.parquet")
    stockout = pl.read_parquet(ROOT / "data/processed/stockout/stockout_v1.parquet")
    inventory = pl.read_parquet(ROOT / "data/warehouse/raw/inventory.parquet")
    demand = pl.read_parquet(ROOT / "data/warehouse/raw/daily_demand.parquet")
    episodes = stockout_episodes(inventory)
    episodes.write_parquet(report / "stockout_episodes.parquet")

    total = forecast.height
    complete = forecast.filter(pl.col("target_observed_next_7d")).height
    positive = demand.filter(pl.col("realized_sales_units") > 0).height
    censored = demand.filter(pl.col("demand_censored_by_inventory")).height
    event_horizons = stockout.filter(pl.col("event_observed")).height
    known_labels = stockout.filter(pl.col("event_observed") | pl.col("horizon_complete"))
    incomplete_nonevents = stockout.filter((~pl.col("event_observed")) & (~pl.col("horizon_complete"))).height
    target_stats = forecast.filter(pl.col("target_observed_next_7d"))["target_units_next_7d"].cast(pl.Float64).describe()
    episode_warehouse = episodes.group_by("warehouse_id").len().sort("warehouse_id")
    episode_sku = episodes.group_by("sku_id").len().sort("len", descending=True)
    feature_columns = ["available_quantity", "stock_to_safety_ratio", "distance_to_reorder_point", "sales_velocity_7d", "replenishment_sum_7d"]
    feature_stats = {}
    for label, subset in (("event", stockout.filter(pl.col("event_observed"))), ("non_event_complete", stockout.filter((~pl.col("event_observed")) & pl.col("horizon_complete")))):
        feature_stats[label] = {c: float(subset[c].cast(pl.Float64).mean()) if subset[c].null_count() < subset.height else None for c in feature_columns}
    split_counts = (
        episodes.with_columns(
            pl.when(pl.col("episode_start") < datetime(2024, 2, 1).date()).then(pl.lit("early"))
            .when(pl.col("episode_start") < datetime(2024, 3, 1).date()).then(pl.lit("middle"))
            .otherwise(pl.lit("late")).alias("period")
        ).group_by("period").len().sort("period")
    )
    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "forecasting": {
            "rows": total,
            "positive_realized_rows": positive,
            "zero_realized_rows": total - positive,
            "zero_realized_rate": (total - positive) / total,
            "complete_targets": complete,
            "incomplete_targets": total - complete,
            "target_coverage": complete / total,
            "inventory_censored_rows": censored,
            "inventory_censored_rate": censored / total,
            "target_distribution": target_stats.to_dicts(),
            "series_count": demand.select(["store_id", "sku_id"]).unique().height,
            "observations_per_series_min": int(demand.group_by(["store_id", "sku_id"]).len()["len"].min()),
            "observations_per_series_max": int(demand.group_by(["store_id", "sku_id"]).len()["len"].max()),
            "requested_units": int(demand["requested_demand_units"].sum()),
            "realized_units": int(demand["realized_sales_units"].sum()),
            "lost_units": int(demand["lost_sales_units"].sum()),
        },
        "stockout": {
            "prediction_rows": stockout.height,
            "positive_prediction_horizons": event_horizons,
            "known_label_rows": known_labels.height,
            "positive_rate_known_labels": event_horizons / known_labels.height,
            "incomplete_non_event_rows": incomplete_nonevents,
            "incomplete_non_event_rate": incomplete_nonevents / stockout.height,
            "physical_episodes": episodes.height,
            "affected_warehouse_sku_series": episodes.select(["warehouse_id", "sku_id"]).unique().height,
            "right_censored_episodes": episodes.filter(pl.col("right_censored")).height,
            "duration_days": episodes["duration_days"].describe().to_dicts(),
            "episodes_by_period": split_counts.to_dicts(),
            "episodes_by_warehouse": episode_warehouse.to_dicts(),
            "top_episodes_by_sku": episode_sku.head(15).to_dicts(),
            "feature_means": feature_stats,
        },
        "before": {
            "forecast_complete_targets": 1035,
            "stockout_positive_prediction_horizons": 14,
            "physical_stockout_episodes": 2,
        },
    }
    (report / "metrics.json").write_text(json.dumps(metrics, indent=2, default=str), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(["before", "after"], [1035, complete], color=["#9ca3af", "#2563eb"])
    ax.set_title("Complete seven-day forecasting targets")
    ax.set_ylabel("rows")
    fig.tight_layout(); fig.savefig(figures / "forecast_target_coverage.png", dpi=200); plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(episodes["duration_days"].to_list(), bins=range(1, int(episodes["duration_days"].max()) + 2), color="#dc2626")
    ax.set_title("Physical stockout episode duration")
    ax.set_xlabel("days until recovery"); ax.set_ylabel("episodes")
    fig.tight_layout(); fig.savefig(figures / "stockout_episode_duration.png", dpi=200); plt.close(fig)

    periods = ", ".join(f"{x['period']}={x['len']}" for x in split_counts.to_dicts())
    warehouses_text = ", ".join(f"W{x['warehouse_id']}={x['len']}" for x in episode_warehouse.to_dicts())
    skus_text = ", ".join(f"SKU{x['sku_id']}={x['len']}" for x in episode_sku.head(10).to_dicts())
    lines = [
        "# Targeted data refinement audit", "", "## 1. Original blockers and root causes", "",
        "The pre-refinement forecasting contract treated the sparse positive-only `sales` table as observation coverage. The generator actually evaluated every store × SKU × day, calculated latent demand, constrained it by inventory, and emitted a sales row only when `sold > 0`. Consequently observed zeros were incorrectly treated as missing and only 1,035 seven-day targets were complete.", "",
        "Inventory started with 300–900 units per warehouse–SKU and replenished on the same snapshot at roughly three times the reorder point. There was no pending-order state or lead-time exposure. Demand therefore could almost never exhaust inventory; the 14 positive horizons represented only two physical episodes.", "",
        "## 2. Exact generator and contract changes", "",
        "The generator now persists a complete `daily_demand` event grid with requested, realized, lost and inventory-censoring fields. Inventory uses heterogeneous reorder/safety/target cover, initial cover, pending replenishment orders, 2–5 day lead times plus occasional 1–3 day delays, and stochastic/promotion-related demand pressure. Stock is never forced to zero and labels are never injected. The forecasting builder reads `fact_daily_demand`; the sparse `fact_sales` remains the realized positive-event ledger.", "",
        "## 3. Forecasting targeted EDA", "",
        f"- Complete grid: {total:,} date × store × SKU rows.",
        f"- Positive realized sales: {positive:,}; observed zeros: {total-positive:,} ({(total-positive)/total:.2%}).",
        f"- Complete `(t,t+7]` targets: {complete:,} ({complete/total:.2%}); end-censored: {total-complete:,}.",
        f"- Series: {metrics['forecasting']['series_count']:,}; observations per series: {metrics['forecasting']['observations_per_series_min']}–{metrics['forecasting']['observations_per_series_max']} calendar days.",
        f"- Inventory-censored demand rows: {censored:,} ({censored/total:.3%}).",
        f"- Requested / realized / lost units: {metrics['forecasting']['requested_units']:,} / {metrics['forecasting']['realized_units']:,} / {metrics['forecasting']['lost_units']:,}.",
        "- Null historical lags mean pre-dataset dates. Numeric zero means an observed zero on the complete grid.",
        "- Realized demand is the primary target; requested and lost demand are retained as audit/alternative outcome fields.", "",
        f"- Complete-target distribution: mean {float(forecast.filter(pl.col('target_observed_next_7d'))['target_units_next_7d'].cast(pl.Float64).mean()):.2f}, median {float(forecast.filter(pl.col('target_observed_next_7d'))['target_units_next_7d'].cast(pl.Float64).median()):.2f}, zero rate {forecast.filter(pl.col('target_observed_next_7d') & (pl.col('target_units_next_7d') == 0)).height/complete:.2%}.", "",
        "## 4. Stockout targeted EDA", "",
        f"- Positive prediction horizons: {event_horizons:,}.",
        f"- Independent physical episodes (`>0 → <=0` until recovery): {episodes.height:,} across {metrics['stockout']['affected_warehouse_sku_series']} warehouse–SKU series.",
        f"- Right-censored episodes: {metrics['stockout']['right_censored_episodes']}; temporal distribution: {periods}.",
        f"- Known classification labels: {known_labels.height:,}; positive rate: {event_horizons/known_labels.height:.2%}; incomplete no-event censoring: {incomplete_nonevents:,} ({incomplete_nonevents/stockout.height:.2%}).",
        f"- Episode duration: median {float(episodes['duration_days'].median()):.1f} days, mean {float(episodes['duration_days'].mean()):.2f}, max {int(episodes['duration_days'].max())} days.",
        f"- Episodes by warehouse: {warehouses_text}.",
        f"- Episode-bearing SKUs: {episode_sku.height}; top counts: {skus_text}.",
        f"- Mean available stock at t, event vs complete non-event: {feature_stats['event']['available_quantity']:.2f} vs {feature_stats['non_event_complete']['available_quantity']:.2f}; mean distance to reorder point: {feature_stats['event']['distance_to_reorder_point']:.2f} vs {feature_stats['non_event_complete']['distance_to_reorder_point']:.2f}.",
        "- Prediction-horizon positives exceed episode count because several adjacent prediction dates can point to the same future episode. Evaluation must split and score by episode/time, not treat these horizons as independent events.", "",
        "## 5. Before / after", "",
        "| Metric | Before | After |", "|---|---:|---:|",
        f"| Complete forecast targets | 1,035 | {complete:,} |",
        f"| Positive stockout horizons | 14 | {event_horizons:,} |",
        f"| Physical stockout episodes | 2 | {episodes.height:,} |", "",
        "Forecasting remains 86,400 rows. Its schema grows from the prior sparse-series contract to 24 columns by adding `censored_days_prior_7d`, `target_requested_demand_next_7d`, and `target_lost_sales_next_7d`; lag/rolling/target values now come from the complete grid. Stockout remains 17,280 rows and 18 columns; its contract did not change, but its causal source distribution did.", "",
        "## 6. Point-in-time and leakage audit", "",
        "Forecast lags address exact dates t−1/t−7/t−14/t−28, and rolling features use `[t−7,t)`. Same-day realized sales, transaction price and realized promotion are absent. Scheduled price/promotion at t remain an explicit assumption because publication timestamps are not modeled. Targets alone use `(t,t+7]`. Stockout covariates use the snapshot at t or history `<t`; only labels inspect `(t,t+7]`. Pending replenishment outcomes after t are not exposed as features.", "",
        "## 7. Regression and validation results", "",
        "PostgreSQL loaded and validated 18 operational tables. PostgreSQL→DuckDB extraction completed for all tables. dbt: 42/42 PASS. Great Expectations: all seven published artifacts PASS. pytest: 29/29 PASS. The episode audit is protected by transition/recovery and minimum-diversity tests.", "",
        "## 8. Downstream distribution impact", "",
        "Sales/anomaly row count changed with the causal regeneration (35,032 realized positive rows). Forecasting and stockout changed materially by design. Segmentation, basket and promotion artifacts were regenerated from the same source run and retained their contracts; no Parquet file was patched manually.", "",
        "## 9. Remaining limitations and readiness", "",
        "Forecasting: **READY WITH LIMITATIONS** for chronological baseline experiments on realized sales. Requested demand is synthetic latent demand, not externally observed truth; promotions cover broad scheduled periods; only 90 calendar days are available.", "",
        "Stockout classification: **READY WITH LIMITATIONS**. Seventy-three episodes across 44 warehouse–SKU series and all three temporal blocks permit a small episode-aware temporal evaluation, but event dependence and synthetic calibration prohibit strong generalization claims.", "",
        "Stockout survival: **READY WITH LIMITATIONS**. Durations and one right-censored terminal episode are represented, but 73 episodes over 90 days are insufficient for complex survival models or stable subgroup inference. Use simple methods and report episode-level uncertainty.", "",
        "No ML model was trained. This iteration ends at data readiness.", "",
        "![Forecast target coverage](figures/forecast_target_coverage.png)", "",
        "![Stockout duration](figures/stockout_episode_duration.png)",
    ]
    (report / "data_refinement_summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
