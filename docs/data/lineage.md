# Data lineage

`fmcg.*` in PostgreSQL is the operational source of record. It is copied as immutable-at-run raw tables to `data/warehouse/fmcg.duckdb:raw.*` and matching raw Parquet files. dbt materializes `analytics` staging, intermediate, dimensional, fact and mart models. Polars reads only those analytical models and emits versioned Parquet datasets under `data/processed`.

The realized-event path is `fmcg.sales → raw.sales → stg_sales → int_sales_enriched → fact_sales → marts / anomaly / promotion_performance`. The complete demand path is `fmcg.daily_demand → raw.daily_demand → stg_daily_demand → fact_daily_demand → forecasting`; this preserves requested, realized, lost and inventory-censoring semantics for every date × store × SKU. Inventory follows `fmcg.inventory → raw.inventory → stg_inventory → fact_inventory → mart_inventory_status / stockout`. Order and delivery lines follow the analogous `raw → staging → fact → basket/order marts` path.

No feature table, model output, or replay table is written into the `fmcg` operational schema. Kafka replay writes only `streaming.*`, so a replay can be audited without altering operational facts.
