# Architecture decisions

## Evidence status

UCI Online Retail II is the open transaction donor. The Dunnhumby repository provides a documented/parquet representation but upstream terms require review. The Chad Lines repository has screenshots and an explanation but no source CSV/XLSX; it is educational, not official Coca-Cola data. Instacart uses the CC0-declared `psparks` mirror because the retired competition endpoint returns 404. Favorita uses `evgeniypolin/favorita-grocery-sales-forecasting`; its eight filenames and schemas match the upstream competition, but the mirror has no identified license. M5 uses University of Nicosia's versioned Zenodo record `10.5281/zenodo.10203108`, referenced as the same data class by the official M5 materials; all five canonical files match the Zenodo MD5 checksums. Original competitions remain upstream provenance. Raw mirrors are not redistributable project artifacts.

## Decisions

- `products` and `skus` remain separate. Product expresses formulation/line; SKU expresses package, volume, price and inventory identity.
- Sales grain is one observed `SKU × store × day`. This is compatible with Favorita's intended role, but any weekly-only donor remains a statistical donor and is never expanded into false daily transactions.
- A store is the B2B customer for this simulation. A redundant `customers` table is omitted. Consumer/household IDs from basket donors are lineage/statistical inputs, not enterprise customers.
- Orders model replenishment/commercial baskets and contain multiple SKUs. Sales are daily observations, not fabricated receipt lines. Instacart empirically calibrates basket size and ordering cadence, but the generated baskets are explicitly B2B adaptations.
- Inventory grain is `warehouse × SKU × snapshot date`; explicit replenishment, fulfilled demand and adjustment fields make flow validation possible.
- Price history uses validity intervals. Sales retains the realized unit price as transaction evidence; this is deliberate, not conflicting master data.
- Deliveries and delivery items are retained because partial multi-SKU fulfillment is needed for stockout and lead-time analysis.
- All canonical IDs are generated internally. External identifiers appear only in explicit lineage fields.

## Limitations

The dev generator uses measured priors: Instacart basket quantiles and reorder cadence; Favorita positive-unit quantiles, promotion frequency and returns; M5 nonzero demand frequency and within-series price ratios. Favorita calibration is based on a continuous 2016 subset with 10 stores, 372 items and 455,269 observations. M5 calibration covers all 30,490 series for identity/schema counts and a stratified 1,200-series sample for demand/price distributions. These are donor priors, not copied business records. PostgreSQL 17 runtime loading and validation are recorded in `artifacts/reports/database_validation.md`.

## Operational indexes

- `sales(sku_id, store_id, sale_date)` supports one-series forecasting extracts; `sales(store_id, sale_date)` supports store reporting; the date-only index supports cross-store daily/weekly aggregation.
- `inventory(warehouse_id, sku_id, snapshot_date)` supports stock history and replenishment analysis; `inventory(sku_id, snapshot_date)` supports network-wide SKU checks.
- `orders(store_id, order_date)` supports customer/store ordering history. The `order_items(order_id, sku_id)` unique index already supports order-to-lines joins, so no redundant order-only index is added.
- `product_prices(store_id, sku_id, valid_from, valid_to)` supports effective-price lookup for one SKU/store series.
- promotion dates and delivery store/status indexes support operational filtering. PK and UNIQUE indexes are not duplicated manually.
