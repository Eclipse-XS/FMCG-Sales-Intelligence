# forecasting

- Grain keys: `prediction_date, store_id, sku_id`
- Rows: 86400
- Columns: 24
- Date range: ['2024-01-01', '2024-03-30']
- Target columns: `target_units_next_7d, target_requested_demand_next_7d, target_lost_sales_next_7d, target_observed_next_7d`
- Duplicate grain keys: 0
- Source cutoff: 2024-03-30

The artifact is Parquet and metadata was generated with the same deterministic build.