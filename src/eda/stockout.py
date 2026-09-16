from __future__ import annotations

import matplotlib.pyplot as plt
import polars as pl

from .common import load, numeric_summary, query, save_json, save_report, savefig


def run() -> dict:
    f = load("stockout")
    events = f.filter(pl.col("event_observed"))
    complete_nonevents = f.filter((~pl.col("event_observed")) & pl.col("horizon_complete"))
    incomplete = f.filter(~pl.col("horizon_complete"))
    features = ["stock_quantity", "reserved_quantity", "available_quantity", "reorder_point", "safety_stock", "stock_to_safety_ratio", "distance_to_reorder_point", "sales_velocity_7d", "replenishment_sum_7d"]
    event_summary = numeric_summary(events, features)
    nonevent_summary = numeric_summary(complete_nonevents, features)
    episodes = query("""with x as (select warehouse_id,sku_id,snapshot_date,available_quantity,
      lag(available_quantity) over(partition by warehouse_id,sku_id order by snapshot_date) previous
      from analytics.fact_inventory)
      select count(*) episode_starts,count(distinct warehouse_id||':'||sku_id) affected_series
      from x where available_quantity<=0 and coalesce(previous,1)>0""").row(0)
    by_warehouse = f.group_by("warehouse_id").agg(pl.len().alias("rows"), pl.col("event_observed").sum().alias("events")).sort("warehouse_id")
    by_sku = f.group_by("sku_id").agg(pl.len().alias("rows"), pl.col("event_observed").sum().alias("events"), pl.col("available_quantity").mean().alias("mean_available")).sort(["events", "sku_id"], descending=[True, False])
    by_date = f.group_by("prediction_date").agg(pl.col("event_observed").sum().alias("events"), pl.col("available_quantity").mean().alias("mean_available")).sort("prediction_date")

    plt.figure(figsize=(7, 4.5))
    labels = ["Observed event", "Complete non-event", "Incomplete horizon"]
    values = [events.height, complete_nonevents.height, incomplete.height]
    plt.bar(labels, values, color=["#d73027", "#31688e", "#fdae61"]); plt.yscale("log")
    plt.ylabel("Rows (log scale)"); plt.title("Stockout target and censoring distribution")
    class_fig = savefig("stockout", "class_distribution.png")

    plt.figure(figsize=(8, 4.8))
    plt.boxplot([events["available_quantity"].to_numpy(), complete_nonevents["available_quantity"].to_numpy()], tick_labels=["Future event", "Complete non-event"], showfliers=False)
    plt.ylabel("Available units at t"); plt.title("Available stock by seven-day event outcome")
    stock_fig = savefig("stockout", "available_stock_by_event.png")

    metrics = {
        "rows": f.height, "observed_events": events.height, "event_rate_all": events.height / f.height,
        "complete_non_events": complete_nonevents.height, "incomplete_horizons": incomplete.height,
        "classification_complete_rows": events.height + complete_nonevents.height,
        "classification_event_rate": events.height / (events.height + complete_nonevents.height),
        "censoring_rate": (f.height - events.height) / f.height,
        "event_time_days": numeric_summary(events, ["event_time_days"])["event_time_days"],
        "censor_time_days": numeric_summary(f.filter(~pl.col("event_observed")), ["censor_time_days"])["censor_time_days"],
        "event_feature_summary": event_summary, "complete_non_event_feature_summary": nonevent_summary,
        "physical_stockout_episode_starts": episodes[0], "affected_warehouse_sku_series": episodes[1],
        "warehouse_distribution": by_warehouse.to_dicts(), "sku_distribution": by_sku.to_dicts(), "temporal_distribution": by_date.to_dicts(),
        "generator_evidence": "initial stock 300-900; reorder trigger below reorder point; replenishment is 3x reorder point only when a five-day modular condition is met",
    }
    save_json("stockout", metrics)
    lines = ["# Stockout EDA", "", "## Target distribution", "", f"- Observed seven-day event rows: {events.height:,} ({events.height/f.height:.4%} of all rows)", f"- Complete non-event horizons: {complete_nonevents.height:,}", f"- Incomplete horizons: {incomplete.height:,}", f"- Event rate among complete/evaluable horizons: {metrics['classification_event_rate']:.4%}", f"- Physical zero-stock episode starts: {episodes[0]} across {episodes[1]} warehouse–SKU series", "", "The 14 positive labels are overlapping prediction horizons around a much smaller number of physical stockout episodes. They are not 14 independent events.", "", "## Generator evidence", "", "Inventory starts at 300–900 units. Replenishment adds three reorder-point quantities when stock is below reorder point and a deterministic five-day condition is satisfied. That combination strongly suppresses stockouts. The low event count is therefore mainly a synthetic-generation artifact, not evidence of a realistically calibrated rare-event process.", "", "## Readiness", "", "- **Stockout Classification: NOT READY.** Fourteen highly dependent positive rows cannot support stable supervised estimation or honest validation. Oversampling would replicate information, not create events.", "- **Stockout Survival: NOT READY.** Censoring is represented correctly, but there are too few independent events to estimate a useful event-time relationship.", "", "Recommendation for a later data-generation phase: calibrate initial stock, replenishment size/delay and demand pressure to generate more independent stockout episodes. Do not modify the generator inside EDA.", "", f"![Class distribution](../{class_fig})", "", f"![Available stock](../{stock_fig})"]
    save_report("stockout", lines)
    return metrics
