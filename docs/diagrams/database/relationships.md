# Аудит FK і cardinality

Джерело: `platform/postgres/schema.sql`. Усі кінці child — `0..N`; PK/UNIQUE на одному FK, який обмежував би його до одного child, відсутній.

| Child FK | Referenced PK | Батьків на child | Дочірніх на parent | ON DELETE | ON UPDATE |
|---|---|---|---|---|---|
| `categories.parent_category_id` | `categories.category_id` | 0..1 | 0..N | NO ACTION | NO ACTION |
| `products.category_id` | `categories.category_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `products.brand_id` | `brands.brand_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `skus.product_id` | `products.product_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `stores.region_id` | `regions.region_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `warehouses.region_id` | `regions.region_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `promotion_skus.promotion_id` | `promotions.promotion_id` | 1 | 0..N | CASCADE | NO ACTION |
| `promotion_skus.sku_id` | `skus.sku_id` | 1 | 0..N | CASCADE | NO ACTION |
| `promotion_stores.promotion_id` | `promotions.promotion_id` | 1 | 0..N | CASCADE | NO ACTION |
| `promotion_stores.store_id` | `stores.store_id` | 1 | 0..N | CASCADE | NO ACTION |
| `product_prices.store_id` | `stores.store_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `product_prices.sku_id` | `skus.sku_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `orders.store_id` | `stores.store_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `order_items.order_id` | `orders.order_id` | 1 | 0..N | CASCADE | NO ACTION |
| `order_items.sku_id` | `skus.sku_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `deliveries.order_id` | `orders.order_id` | 0..1 | 0..N | NO ACTION | NO ACTION |
| `deliveries.warehouse_id` | `warehouses.warehouse_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `deliveries.store_id` | `stores.store_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `delivery_items.delivery_id` | `deliveries.delivery_id` | 1 | 0..N | CASCADE | NO ACTION |
| `delivery_items.sku_id` | `skus.sku_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `inventory.warehouse_id` | `warehouses.warehouse_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `inventory.sku_id` | `skus.sku_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `sales.store_id` | `stores.store_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `sales.sku_id` | `skus.sku_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `sales.promotion_id` | `promotions.promotion_id` | 0..1 | 0..N | NO ACTION | NO ACTION |
| `daily_demand.store_id` | `stores.store_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `daily_demand.sku_id` | `skus.sku_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `daily_demand.warehouse_id` | `warehouses.warehouse_id` | 1 | 0..N | NO ACTION | NO ACTION |
| `daily_demand.promotion_id` | `promotions.promotion_id` | 0..1 | 0..N | NO ACTION | NO ACTION |

## PK та UNIQUE

| Таблиця | PK | UNIQUE groups |
|---|---|---|
| categories | category_id | U1: (category_name, parent_category_id) |
| brands | brand_id | U1: (brand_name) |
| products | product_id | U1: (brand_id, product_name) |
| skus | sku_id | U1: (sku_code); U2: (product_id, package_type, volume_ml, flavor) |
| regions | region_id | U1: (country, region_name) |
| stores | store_id | U1: (external_store_code) |
| warehouses | warehouse_id | U1: (warehouse_code) |
| promotions | promotion_id | — |
| promotion_skus | promotion_id, sku_id | — |
| promotion_stores | promotion_id, store_id | — |
| product_prices | price_id | U1: (store_id, sku_id, valid_from) |
| orders | order_id | U1: (order_code) |
| order_items | order_item_id | U1: (order_id, sku_id) |
| deliveries | delivery_id | U1: (delivery_code) |
| delivery_items | delivery_id, sku_id | — |
| inventory | inventory_id | U1: (snapshot_date, warehouse_id, sku_id) |
| sales | sale_id | U1: (sale_date, store_id, sku_id) |
| daily_demand | demand_observation_id | U1: (observation_date, store_id, sku_id) |
