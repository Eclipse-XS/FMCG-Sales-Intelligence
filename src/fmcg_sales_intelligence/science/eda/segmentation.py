from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

from .common import load, numeric_summary, save_json, save_report, savefig


def run() -> dict:
    f = load("segmentation")
    numerical = ["revenue_30d", "units_30d", "profit_30d", "active_skus_30d", "average_price_30d", "promotion_unit_share_30d", "revenue_volatility_30d", "floor_area_m2"]
    summary = numeric_summary(f, numerical)
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = np.corrcoef(np.column_stack([f[c].cast(pl.Float64).to_numpy() for c in numerical]), rowvar=False)
    stability = f.sort(["store_id", "snapshot_date"]).with_columns([
        pl.col("revenue_30d").cast(pl.Float64).pct_change().over("store_id").alias("revenue_change"),
        pl.col("units_30d").cast(pl.Float64).pct_change().over("store_id").alias("units_change"),
    ])

    plt.figure(figsize=(8, 6)); image = plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.xticks(range(len(numerical)), numerical, rotation=75, ha="right", fontsize=8); plt.yticks(range(len(numerical)), numerical, fontsize=8)
    plt.colorbar(image, label="Pearson correlation"); plt.title("Store-feature correlation matrix")
    corr_fig = savefig("segmentation", "feature_correlations.png")

    plt.figure(figsize=(8, 4.8))
    for store in range(1, 6):
        x = f.filter(pl.col("store_id") == store).sort("snapshot_date")
        plt.plot(x["snapshot_date"], x["revenue_30d"].cast(pl.Float64), marker="o", label=f"Store {store}")
    plt.xlabel("Snapshot"); plt.ylabel("30-day revenue"); plt.title("Snapshot stability: representative stores"); plt.legend(ncol=2)
    stability_fig = savefig("segmentation", "snapshot_stability.png")

    metrics = {
        "rows": f.height, "unique_stores": f["store_id"].n_unique(), "snapshots": f["snapshot_date"].n_unique(),
        "numerical_summary": summary, "correlation_matrix": {a: {b: float(corr[i, j]) for j, b in enumerate(numerical)} for i, a in enumerate(numerical)},
        "categorical_cardinality": {c: f[c].n_unique() for c in ["store_type", "channel", "region_id"]},
        "categorical_composition": {c: f.group_by(c).len().sort(c).to_dicts() for c in ["store_type", "channel", "region_id"]},
        "snapshot_change": numeric_summary(stability.drop_nulls(["revenue_change", "units_change"]), ["revenue_change", "units_change"]),
        "features_requiring_scaling": numerical,
    }
    save_json("segmentation", metrics)
    lines = ["# Store segmentation EDA", "", f"The contract contains {f.height} snapshots but only {f['store_id'].n_unique()} independent stores. Repeated snapshots improve temporal characterization; they do not create 60 independent entities.", "", "All numerical features differ materially in scale, so distance-based clustering will require scaling. Revenue, units and profit are structurally correlated; feature redundancy should be checked before clustering. Floor area is static per store and may dominate Euclidean distance if left unscaled.", "", "Store type, channel and region are categorical/entity attributes and must not be treated as ordinal integers. Encoding choices belong to modeling, not EDA.", "", "## Readiness", "", "**READY WITH LIMITATIONS.** Twenty stores can support an illustrative segmentation experiment but not a stable high-dimensional market taxonomy. Cluster stability must be assessed by store, not by randomly splitting the 60 snapshots. `segment_assignment` remains **NOT READY** until a clustering model creates assignments.", "", f"![Correlations](../{corr_fig})", "", f"![Stability](../{stability_fig})"]
    save_report("segmentation", lines)
    return metrics
