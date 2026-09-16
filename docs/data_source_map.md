# Data source map

| Canonical field | Donor field/concept | Treatment | Assumption |
|---|---|---|---|
| `categories.category_name` | Favorita `family`; FMCG `Category` | transformed/synthetic | beverage taxonomy is canonical, not copied IDs |
| `brands.brand_name` | FMCG `Brand`; public portfolio metadata | public factual or synthetic | provenance stored per row |
| `products.product_name` | FMCG product/segment concepts | synthetic | formulation/line above SKU |
| `skus.*` | FMCG SKU, package, volume | synthetic from categorical distributions | sellable unit |
| `stores.*` | Favorita stores; FMCG channel/region | transformed/synthetic | canonical store IDs |
| `sales.quantity_units` | Favorita `unit_sales`; FMCG daily sales | empirical distribution, then generated | grain stays store/SKU/day |
| `sales.unit_price` | M5 `sell_price`; FMCG selling price | empirical distribution, then generated | realized transaction price |
| `sales.promotion_id` | Favorita `onpromotion`; Dunnhumby causal data | inferred mapping | association is not causal proof |
| `product_prices.*` | M5 store/item/week/sell_price | transformed intervals | no cross-dataset ID merge |
| `orders/order_items` | UCI Invoice lines; Instacart `orders`, `order_products__prior/train`; Dunnhumby baskets | Instacart-calibrated basket quantiles and generated canonical baskets | store is B2B buyer; no external IDs reused |
| `inventory.reorder_point` | inventory donors reorder fields | demand-class distribution | derived from demand class, not independent noise |
| `inventory.stock_quantity` | prior stock + arrivals − fulfillment ± adjustment | synthetic causal state | nonnegative, constrained demand |
| `deliveries.*` | inventory donor lead time | generated process | supports partial deliveries |
| `promotions.*` | Favorita, Dunnhumby, FMCG promotion fields | generated from profiled durations/reach | uplift remains probabilistic |

Every row-level transformation must carry `provenance`, plus `external_source/external_id` where lineage remains meaningful.

Measured Instacart, Favorita and M5 parameters are stored in `data/metadata/donor_calibration.json`. Favorita came from a public Kaggle mirror with the original competition retained as upstream provenance. M5 came from the University of Nicosia Zenodo distribution and passed published MD5 verification.
