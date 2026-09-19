from __future__ import annotations

import matplotlib.pyplot as plt

from .common import ARTIFACTS, overview, save_json, save_report, savefig


def run() -> dict:
    metrics = overview()
    plt.figure(figsize=(10, 4.8))
    plt.bar([x.replace("_", "\n") for x in ARTIFACTS], [metrics[x]["rows"] for x in ARTIFACTS], color="#31688e")
    plt.yscale("log")
    plt.ylabel("Rows (log scale)")
    plt.title("EDA artifact sizes")
    figure = savefig("general", "artifact_sizes.png")
    lines = ["# General data understanding", "", "All identifier columns are entity keys, not continuous measurements. Integer storage does not make `store_id`, `sku_id`, `warehouse_id`, `promotion_id`, `order_id`, or `region_id` quantitative.", "", "| Artifact | Rows | Columns | Date range | Duplicate keys |", "|---|---:|---:|---|---:|"]
    for name in ARTIFACTS:
        x = metrics[name]
        lines.append(f"| {name} | {x['rows']:,} | {x['columns']} | {x['date_range'][0]}–{x['date_range'][1]} | {x['duplicate_business_keys']} |")
    lines += ["", "## Feature taxonomy", "", "- Numerical: prices, quantities, lags, rolling statistics, inventory, revenue and profit.", "- Categorical: brand, category, store type, channel, promotion and discount type.", "- Binary: scheduled promotion, stockout/event indicators, horizon completeness.", "- Temporal: prediction, snapshot, event, order and promotion dates.", "- Identifiers: store, SKU, warehouse, promotion, order and region IDs.", "", f"![Artifact sizes](../{figure})"]
    save_json("general", metrics)
    save_report("general", lines)
    return metrics
