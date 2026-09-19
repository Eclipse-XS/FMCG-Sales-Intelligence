# Canonical contracts V1

The authoritative machine registry is `config/contracts/registry_v1.yaml`. It defines 11 contracts: `sales_daily`, `sku_master`, `locations`, `prices`, `inventory_snapshots`, `deliveries`, `orders`, `order_items`, `promotions`, `promotion_stores`, and `promotion_skus`.

Each record provides version, grain, business key, fields, nullability, units, semantics, consumers, and source of truth. Source aliases are mapped before feature construction; canonical persisted identifiers such as `store_id` and `sku_id` remain stable. Breaking contract changes require a new major contract version. Compatible optional-field additions may retain the major version with documented revision.

Capability dependencies are explicit: basket requires orders/items; stockout requires inventory/deliveries; promotion requires campaign eligibility; segmentation requires location behavior; missing concepts are not fabricated.

