# ML data requirements

| Capability | Source tables / keys | Grain and target | Candidate inputs | Missing/synthetic assumptions |
|---|---|---|---|---|
| Demand forecast | `sales` + SKU/product/category + store + prices/promotions | SKU/store/day; future quantity | calendar, realized price, promotion, hierarchy | holidays/weather need analytical enrichment |
| Stockout risk | inventory + deliveries + sales | warehouse/SKU/day; stockout within horizon | stock, demand history, open deliveries, lead time | censored demand must be estimated |
| Store segmentation | stores + aggregated sales/orders | store/window; unsupervised | mix, frequency, value, volatility | no operational cluster column |
| Segment assignment | analytical labels + store aggregates | store; derived label | same stable aggregates | labels live outside OLTP |
| Anomaly detection | sales | SKU/store/day; anomaly score | seasonal residuals, price, promo | score outside OLTP |
| Basket rules | orders + order_items | order/SKU | SKU co-occurrence | Instacart gives empirical basket-size/reorder priors; B2B composition is still synthetic |
| Promotion analysis | sales + promotion junctions + prices | promotion/SKU/store/day; incremental units/revenue | pre-period, controls, price | observational data do not identify causality alone |
| BI | sales + dimensions | week/store/category/SKU | revenue, units, margin | calendar dimension may be added analytically |
