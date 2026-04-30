# Dataset contracts

All artifacts are synthetic, versioned Parquet outputs under `data/processed/`. Forecast prediction time is the **start of day `t`**. Forecast features use only facts strictly earlier than `t` plus price/promotion schedules effective at `t`; target joins are explicitly separate. Anomaly detection is a distinct post-event contract.

| Dataset | Grain | Target / formulation | Cutoff and leakage rule |
|---|---|---|---|
| forecasting | prediction_date × store × SKU | `target_units_next_7d`, `target_observed_next_7d` | lags/7d windows use dates `< t`; target sums `(t,t+7]` only when all seven dates are observed |
| stockout | snapshot_date × warehouse × SKU | `stockout_within_7d`, `event_observed`, `event_time_days`, `censor_time_days` | features use snapshots/sales `< t`; labels search `(t,t+7]`; `horizon_complete` distinguishes end-of-data censoring |
| segmentation | snapshot_date × store | unsupervised feature contract | 30d aggregates use `[t-30d,t)` |
| segment_assignment | snapshot_date × store | none; exact alias of segmentation features | pre-clustering compatibility artifact; no target or cluster label |
| anomaly | event_date × store × SKU | unsupervised / later residual | post-event contract; explicitly named realized event fields; no synthetic anomaly label |
| basket | order × SKU | association-rule long representation | order context only; contextual fields are not implicit items |
| promotion_performance | promotion × store × SKU | before/during/after metrics | descriptive analysis, not causal effect |

The generator evaluates every date × store × SKU combination in `daily_demand`. A missing row in the positive-only `sales` fact therefore means **observed zero realized sales**, not an unobserved day. It may still be inventory-censored latent demand. `requested_demand_units = realized_sales_units + lost_sales_units`, and `demand_censored_by_inventory` marks positive lost demand. Forecast lags and targets use the complete `daily_demand` grid. Null lag values mean the requested historical date predates the dataset; zero means an observed zero. A forecasting target is published when every date in `(t,t+7]` is present; `target_observed_days_next_7d` exposes the count. `target_units_next_7d` is realized demand, while `target_requested_demand_next_7d` and `target_lost_sales_next_7d` preserve the latent-demand audit. Stockout uses `available_quantity <= 0`; every no-event row has an explicit `censor_time_days`, including complete seven-day horizons.

A physical stockout episode starts on a transition from `available_quantity > 0` to `available_quantity <= 0` and ends on the first subsequent recovery to `available_quantity > 0`. Multiple positive prediction horizons pointing at one episode are not counted as multiple operational events.

`scheduled_selling_price` is the price interval effective at the start of `t`. `scheduled_promotion_id` and `scheduled_is_promo` come from promotion/store/SKU schedules, never from the realized sale row. This assumes those schedules were committed before scoring; the operational schema has no schedule-publication timestamp, so that assumption cannot be proven historically.

Each `.metadata.json` records version, cutoff, schema, row count, grain keys and targets. Temporal splits must be chronological; random train/test split is prohibited for forecasting, stockout and anomaly tasks.
