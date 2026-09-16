# Feature catalog

| Feature | Family | Grain | Availability | Used by |
|---|---|---|---|---|
| `lag_1`, `lag_7`, `lag_14`, `lag_28` | demand | store × SKU × date | exact historical date `< t` | forecasting, anomaly |
| `rolling_mean_7d`, `rolling_std_7d`, `sales_velocity_7d` | demand | store × SKU × date | sales in `[t-7d,t)` | forecasting, anomaly, stockout |
| `scheduled_selling_price` | pricing | store × SKU × date | validity interval containing start of `t` | forecasting |
| `scheduled_promotion_id`, `scheduled_is_promo` | promotion schedule | store × SKU × date | scheduled interval containing start of `t` | forecasting |
| `censored_days_prior_7d` | demand censoring | store × SKU × date | count of censored observations in `[t-7d,t)` | forecasting |
| `event_observed_units`, `event_transaction_unit_price`, `event_is_promo` | realized event | store × SKU × event date | available only after the sale event | anomaly |
| `stock_to_safety_ratio`, `distance_to_reorder_point` | inventory | warehouse × SKU × date | inventory snapshot at `t` | stockout |
| `replenishment_sum_7d` | inventory | warehouse × SKU × date | snapshots `[t-7d,t)` | stockout |
| `revenue_30d`, `units_30d`, `profit_30d` | store | store × snapshot | sales `[t-30d,t)` | segmentation, assignment |
| `active_skus_30d`, `promotion_unit_share_30d`, `revenue_volatility_30d` | store | store × snapshot | sales `[t-30d,t)` | segmentation, assignment |

`target_units_next_7d` is the sum of realized sales over `(t,t+7]`. `target_requested_demand_next_7d` is the corresponding latent/requested demand and `target_lost_sales_next_7d` is its inventory-censored component. All are null unless all seven store–SKU dates are observed, and none is a model feature. Forecast-residual anomaly features do not exist until an out-of-sample forecasting model is trained.
