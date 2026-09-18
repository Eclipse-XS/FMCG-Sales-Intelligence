# Data and Model Dependency Map

```mermaid
flowchart TD
  GEN[Synthetic generator<br/>executed local] --> PG[(PostgreSQL operational schema<br/>executed local)]
  KAFKA[Kafka replay simulation<br/>implemented demo; runtime evidence absent] -. replay .-> PG
  PG --> EXT[Local extractor<br/>executed]
  AIRBYTE[Airbyte config<br/>not executed] -. planned .-> BQ[(BigQuery<br/>not executed)]
  EXT --> DUCK[(DuckDB raw)] --> DBT[dbt warehouse/marts<br/>executed]
  DBT --> DS[Processed Parquet datasets<br/>GE validated; DVC owned]
  DS --> F[Forecasting]
  DS --> SC[Stockout classification]
  DS --> SS[Stockout survival]
  DS --> SEG[Segmentation]
  DS --> AN[Anomaly]
  DS --> BAS[Basket]
  DS --> PRO[Promotion]
  SEG -. unstable pseudo-labels .-> BLOCK[Segment Assignment<br/>BLOCKED]
  F --> CA[Canonical DVC artifacts]
  SC --> CA
  SS --> CA
  SEG --> CA
  AN --> CA
  BAS --> CA
  PRO --> CA
  CA --> SERVE[Future batch/API serving<br/>Forecasting + Stockout classification]
  CA --> BI[Future BI marts<br/>reviewed analytical outputs]
  CA --> REVIEW[Human review<br/>segments/anomalies/rules/promotions]
```

There are no model-to-model runtime dependencies among implemented cores. Stockout models use their own historical velocity and inventory features, not Forecasting predictions. Anomaly V1 cannot consume Forecasting V1 residuals because Forecasting predicts a seven-day aggregate and Anomaly operates on observed event-day rows. Segment Assignment is the only explicitly blocked downstream dependency.

Semantic glossary:

- `realized_sales_units`: observed fulfilled sales.
- `requested_demand_units`: synthetic latent/requested demand context, not interchangeable with sales.
- `target_units_next_7d`: future realized units in `(t,t+7]`.
- `stockout_within_7d`: occurrence of the first future stockout within `(t,t+7]`.
- survival event: first future physical stockout onset for an at-risk row.
- anomaly candidate: unsupervised review candidate, not confirmed fraud/error.
- segment pseudo-label: exploratory cluster membership, not a validated supervised target.
- association rule: co-occurrence statistic, not recommendation or causation.
- promotion descriptive change: eligible matched-window observed difference, not causal uplift.
