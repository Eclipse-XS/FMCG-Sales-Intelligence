from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

from .common import load, numeric_summary, save_json, save_report, savefig


def run() -> dict:
    f = load("anomaly").with_columns(
        ((pl.col("event_observed_units") - pl.col("rolling_mean_7d")) / pl.col("rolling_std_7d").replace(0, None)).alias("historical_zscore")
    )
    scored = f.drop_nulls("historical_zscore")
    candidates = scored.filter(pl.col("historical_zscore").abs() >= 3)
    promo = f.group_by("event_is_promo").agg(pl.len().alias("rows"), pl.col("event_observed_units").mean().alias("mean_units"))
    price_by_sku = f.group_by("sku_id").agg(pl.col("event_transaction_unit_price").mean().alias("mean"), pl.col("event_transaction_unit_price").std().alias("std"))

    plt.figure(figsize=(8, 4.8)); plt.hist(scored["historical_zscore"].clip(-8, 8).to_numpy(), bins=40, color="#31688e", edgecolor="white")
    plt.axvline(-3, color="#d73027", linestyle="--"); plt.axvline(3, color="#d73027", linestyle="--")
    plt.xlabel("Historical z-score (clipped for display)"); plt.ylabel("Events"); plt.title("Post-event deviation from trailing history")
    z_fig = savefig("anomaly", "historical_deviation.png")

    top = f.group_by("sku_id").agg(pl.col("event_observed_units").std().alias("volatility")).sort("volatility", descending=True).head(12)
    plt.figure(figsize=(8, 4.8)); plt.bar([str(x) for x in top["sku_id"]], top["volatility"], color="#35b779")
    plt.xlabel("SKU ID"); plt.ylabel("Standard deviation of units"); plt.title("Highest-variability SKUs")
    vol_fig = savefig("anomaly", "high_variability_skus.png")

    metrics = {"rows": f.height, "scorable_historical_z_rows": scored.height, "absolute_z_ge_3_candidates": candidates.height,
        "candidate_fraction": candidates.height / scored.height, "event_summary": numeric_summary(f, ["event_observed_units", "event_transaction_unit_price", "lag_1", "lag_7", "rolling_mean_7d", "rolling_std_7d"]),
        "promo_comparison": promo.to_dicts(), "sku_price_variability": numeric_summary(price_by_sku, ["std"])["std"], "verified_anomalies": 0}
    save_json("anomaly", metrics)
    lines = ["# Anomaly detection EDA", "", f"There are {candidates.height:,} statistical/contextual candidates with |historical z-score| ≥ 3 among {scored.height:,} rows with a usable rolling standard deviation. These are not verified anomalies.", "", "The contract is post-event: units, realized transaction price and realized promotion state are known when scoring. Missing rolling statistics are structural early/sparse-history cases. No supervised label exists.", "", "Forecast residuals would be useful later, but only if generated from out-of-sample forecasts. In-sample residuals would leak model fit and understate anomaly magnitude.", "", "## Readiness", "", "**READY WITH LIMITATIONS.** Unsupervised/statistical candidate ranking is feasible. Supervised anomaly classification is not. Evaluation will require injected anomalies with a documented mechanism or human-reviewed labels.", "", f"![Deviation](../{z_fig})", "", f"![Volatility](../{vol_fig})"]
    save_report("anomaly", lines)
    return metrics
