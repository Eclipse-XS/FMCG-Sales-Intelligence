# Market Basket / Association Rule Mining V1

An `order_id` is one basket and each distinct SKU is binary presence regardless of quantity. Brand and category baskets are deduplicated within order. Support is based on valid orders, not order-item rows.

Apriori is the correctness baseline and FP-Growth the canonical scalable implementation. Both use the same frozen support threshold and must return equivalent frequent itemsets. Canonical rules have one-item antecedent and consequent, minimum support/confidence/lift, deterministic IDs, and lexicographic ranking by lift, support, then confidence.

Monthly and operational-context diagnostics describe stability. Segmentation pseudo-labels are excluded because they remain `NOT_READY`. Rules are `UNREVIEWED` associations, not causal effects, recommendations, or supervised predictions.

The synthetic generator samples basket sizes from donor-calibrated quantiles and SKUs without replacement using weights proportional to `1 / sku_id^0.7`. Consequently, recovered popularity and co-occurrence patterns partly reflect generator mechanics.

Reproduce with `.venv\Scripts\python.exe -m fmcg_sales_intelligence.science.cli run --task basket --output artifacts/canonical/basket_v1 --experiment-id basket_v1_canonical --overwrite`.
