from __future__ import annotations

import matplotlib.pyplot as plt
import polars as pl

from .common import load, numeric_summary, query, save_json, save_report, savefig


def run() -> dict:
    f = load("promotion_performance").with_columns([
        (pl.col("promo_units") - pl.col("baseline_units")).alias("units_uplift_absolute"),
        (((pl.col("promo_units") - pl.col("baseline_units")) / pl.col("baseline_units").replace(0, None)).cast(pl.Float64)).alias("units_uplift_percent"),
        (((pl.col("post_units") - pl.col("baseline_units")) / pl.col("baseline_units").replace(0, None)).cast(pl.Float64)).alias("post_vs_baseline"),
    ])
    valid = f.drop_nulls(["baseline_units", "promo_units"])
    by_promo = f.group_by("promotion_id").agg(pl.len().alias("rows"), pl.col("baseline_units").null_count().alias("baseline_null"), pl.col("post_units").null_count().alias("post_null"), pl.col("promo_units").sum().alias("promo_units"), pl.col("promo_revenue").sum().alias("promo_revenue"), pl.col("promo_profit").sum().alias("promo_profit")).sort("promotion_id")
    enriched = query("""select p.*,d.brand_name,d.category_name from read_parquet('data/processed/promotion_performance/promotion_performance_v1.parquet') p join analytics.dim_product d using(sku_id)""")
    by_category = enriched.group_by("category_name").agg(pl.col("promo_units").sum().alias("promo_units"), pl.col("promo_revenue").sum().alias("promo_revenue")).sort("promo_units", descending=True)
    by_context = {c: enriched.group_by(c).agg(pl.col("promo_units").sum().alias("promo_units"), pl.col("promo_revenue").sum().alias("promo_revenue"), pl.col("promo_profit").sum().alias("promo_profit")).sort(c).to_dicts() for c in ["brand_name", "region_id", "store_type", "channel"]}

    plt.figure(figsize=(8, 4.8));
    plot = valid.filter(pl.col("units_uplift_percent").is_finite())["units_uplift_percent"].cast(pl.Float64).clip(-3, 3)
    plt.hist(plot.to_numpy(), bins=35, color="#31688e", edgecolor="white"); plt.axvline(0, color="black", linewidth=1)
    plt.xlabel("(Promo units − baseline units) / baseline units, clipped"); plt.ylabel("Promotion–store–SKU rows"); plt.title("Descriptive during-vs-before unit difference")
    uplift_fig = savefig("promotion", "descriptive_uplift.png")

    plt.figure(figsize=(8, 4.8)); plt.bar([str(x) for x in by_promo["promotion_id"]], by_promo["promo_revenue"].cast(pl.Float64), color="#35b779")
    plt.xlabel("Promotion ID"); plt.ylabel("Revenue during scheduled window"); plt.title("Revenue observed during each promotion window")
    revenue_fig = savefig("promotion", "promotion_revenue.png")

    metrics = {"rows": f.height, "baseline_null_rows": int(f["baseline_units"].null_count()), "post_null_rows": int(f["post_units"].null_count()),
        "valid_baseline_rows": valid.height, "derived_metrics": numeric_summary(valid, ["units_uplift_absolute", "units_uplift_percent", "post_vs_baseline"]),
        "by_promotion": by_promo.to_dicts(), "by_category": by_category.to_dicts(), "by_context": by_context}
    save_json("promotion", metrics)
    lines = ["# Promotion performance EDA", "", f"- Rows without baseline history: {metrics['baseline_null_rows']:,} ({metrics['baseline_null_rows']/f.height:.2%})", f"- Rows without post-period history: {metrics['post_null_rows']:,} ({metrics['post_null_rows']/f.height:.2%})", f"- Rows with usable before/during comparison: {valid.height:,}", "", "The first promotion lacks preceding history; the last lacks post-period history. Percentage measures exclude NULL or zero baselines rather than substituting zero.", "", "All comparisons are descriptive: sales during a scheduled window versus preceding/following windows. The data has no untreated control group, randomized assignment, parallel-trend evidence, competitor activity or exogenous-demand controls, so causal promotion effects cannot be estimated.", "", "## Readiness", "", "**READY WITH LIMITATIONS** for descriptive analysis. **NOT READY** for causal effect estimation. A later causal design would require comparable untreated units, pre-trend history, treatment timing variation, confounder controls and preferably randomized or quasi-experimental assignment.", "", f"![Descriptive comparison](../{uplift_fig})", "", f"![Revenue](../{revenue_fig})"]
    save_report("promotion", lines)
    return metrics
