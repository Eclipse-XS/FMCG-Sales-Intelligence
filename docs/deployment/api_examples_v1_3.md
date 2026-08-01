# API examples V1.3

Start the API with `python -m fmcg_sales_intelligence.cli serve` or Docker Compose. These are validated synthetic rows.

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/ready
```

## Forecast

```powershell
$body = @{ rows = @(@{
  lag_1=0; lag_7=4; lag_14=4; lag_28=0; sales_velocity_7d=14.0
  rolling_mean_7d=2.0; rolling_std_7d=2.0; scheduled_selling_price=3.83
  store_id=10; sku_id=39; region_id=2; brand_name='Orchard'
  category_name='Juice'; store_type='convenience'; channel='modern_trade'
}) } | ConvertTo-Json -Depth 4
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/predict/forecast -ContentType application/json -Body $body
```

The target is `target_units_next_7d` over `(t,t+7d]`.

## Stockout classification

```powershell
$body = @{ rows = @(@{
  stock_quantity=71; reserved_quantity=0; available_quantity=71; reorder_point=73
  safety_stock=26; distance_to_reorder_point=-2; replenishment_sum_7d=136.0
  stock_to_safety_ratio=2.730769230769231; sales_velocity_7d=5.5625
  warehouse_id=3; sku_id=6
}) } | ConvertTo-Json -Depth 4
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/predict/stockout -ContentType application/json -Body $body
```

The score is evaluated against the frozen threshold; it is not claimed strongly calibrated.

## Experimental cluster membership

```powershell
$body = @{ rows = @(@{
  store_id=1; revenue_30d=2306.7; average_price_30d=2.6558561643835614
  promotion_unit_share_30d=0.20856201975850713
  revenue_volatility_30d=5.16244240318117
}) } | ConvertTo-Json -Depth 4
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/analytics/segments/assign -ContentType application/json -Body $body
```

This invokes frozen KMeans `predict`. The cluster is exploratory pseudo-labeling, not governed ground truth; centroid distance is not confidence.
