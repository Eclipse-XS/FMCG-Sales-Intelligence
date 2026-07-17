from __future__ import annotations

import matplotlib.pyplot as plt
import polars as pl

from .common import load, numeric_summary, query, save_json, save_report, savefig


def run() -> dict:
    f = load("basket")
    baskets = f.group_by("order_id").agg(pl.len().alias("basket_size"), pl.col("quantity").sum().alias("total_units"))
    sku = f.group_by(["sku_id", "product_name"]).agg(pl.col("order_id").n_unique().alias("orders")).sort("orders", descending=True)
    category = f.group_by("category_name").agg(pl.col("order_id").n_unique().alias("orders"), pl.len().alias("lines")).sort("orders", descending=True)
    pairs = query("""select a.sku_id sku_a,b.sku_id sku_b,count(*) orders,
      count(*)/(select count(distinct order_id) from analytics.fact_order_items)::double support
      from analytics.fact_order_items a join analytics.fact_order_items b on a.order_id=b.order_id and a.sku_id<b.sku_id
      group by 1,2 order by orders desc,sku_a,sku_b limit 20""")
    contexts = f.group_by(["store_type", "channel", "region_id"]).agg(pl.col("order_id").n_unique().alias("orders"), pl.len().alias("lines"))

    plt.figure(figsize=(8, 4.8)); plt.hist(baskets["basket_size"].to_numpy(), bins=range(int(baskets["basket_size"].min()), int(baskets["basket_size"].max()) + 2), color="#31688e", edgecolor="white")
    plt.xlabel("Distinct SKUs per order"); plt.ylabel("Orders"); plt.title("Basket-size distribution")
    basket_fig = savefig("basket", "basket_size_distribution.png")

    top = sku.head(15).sort("orders")
    plt.figure(figsize=(8, 5)); plt.barh([str(x) for x in top["sku_id"]], top["orders"], color="#35b779")
    plt.xlabel("Orders containing SKU"); plt.ylabel("SKU ID"); plt.title("Top 15 SKUs by order frequency")
    sku_fig = savefig("basket", "top_skus.png")

    metrics = {"rows": f.height, "orders": f["order_id"].n_unique(), "skus": f["sku_id"].n_unique(),
        "basket_size": numeric_summary(baskets, ["basket_size"])["basket_size"], "quantity_per_line": numeric_summary(f, ["quantity"])["quantity"],
        "top_skus": sku.head(20).to_dicts(), "category_frequency": category.to_dicts(), "top_pairs": pairs.to_dicts(), "context_counts": contexts.to_dicts(),
        "duplicate_order_sku": int(f.select(["order_id", "sku_id"]).is_duplicated().sum())}
    save_json("basket", metrics)
    max_support = float(pairs["support"].max()) if pairs.height else 0
    lines = ["# Market basket EDA", "", f"- Orders: {metrics['orders']:,}", f"- SKUs: {metrics['skus']}", f"- Lines: {f.height:,}", f"- Mean basket size: {metrics['basket_size']['mean']:.2f}; median: {metrics['basket_size']['median']:.0f}; range: {metrics['basket_size']['min']:.0f}–{metrics['basket_size']['max']:.0f}", f"- Duplicate order–SKU keys: {metrics['duplicate_order_sku']}", f"- Highest observed pair support: {max_support:.2%}", "", "Popularity is intentionally long-tailed because order generation samples SKUs with weights proportional to `1 / sku_id^0.7`. Co-occurrence counts are descriptive and not yet association rules.", "", "## Readiness", "", "**READY.** Two thousand baskets and 48 items are adequate for an instructional association-rule experiment. Future support exploration should start around the empirical pair-frequency range, roughly 0.5%–5%, before confidence/lift filtering; this is a search range, not a tuned choice.", "", f"![Basket size](../{basket_fig})", "", f"![Top SKUs](../{sku_fig})"]
    save_report("basket", lines)
    return metrics
