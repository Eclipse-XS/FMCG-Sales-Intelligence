# Operational database validation

Database: `fmcg`; PostgreSQL `17.11`; overall: **PASS**.

## Row counts

| Table | CSV | Database | Match |
|---|---:|---:|---|
| categories | 6 | 6 | True |
| brands | 6 | 6 | True |
| products | 48 | 48 | True |
| skus | 48 | 48 | True |
| regions | 4 | 4 | True |
| stores | 20 | 20 | True |
| warehouses | 4 | 4 | True |
| promotions | 3 | 3 | True |
| promotion_skus | 144 | 144 | True |
| promotion_stores | 60 | 60 | True |
| product_prices | 12480 | 12480 | True |
| sales | 35032 | 35032 | True |
| daily_demand | 86400 | 86400 | True |
| orders | 2000 | 2000 | True |
| order_items | 24370 | 24370 | True |
| deliveries | 2000 | 2000 | True |
| delivery_items | 24370 | 24370 | True |
| inventory | 17280 | 17280 | True |

## Integrity and business rules

| Check | Violations | Result |
|---|---:|---|
| orphan sales sku | 0 | PASS |
| orphan sales store | 0 | PASS |
| orphan daily demand | 0 | PASS |
| orphan inventory sku | 0 | PASS |
| orphan inventory warehouse | 0 | PASS |
| orphan order items order | 0 | PASS |
| orphan order items sku | 0 | PASS |
| orphan promotion sku mapping | 0 | PASS |
| orphan promotion store mapping | 0 | PASS |
| orphan price | 0 | PASS |
| duplicate sales grain | 0 | PASS |
| duplicate demand grain | 0 | PASS |
| duplicate inventory grain | 0 | PASS |
| duplicate price start grain | 0 | PASS |
| overlapping price periods | 0 | PASS |
| invalid sales numerics | 0 | PASS |
| invalid inventory numerics | 0 | PASS |
| invalid demand reconciliation | 0 | PASS |
| order reconciliation | 0 | PASS |
| inventory flow | 0 | PASS |
| daily demand to inventory reconciliation | 0 | PASS |
| invalid promotion dates | 0 | PASS |
| invalid price dates | 0 | PASS |
| invalid order chronology | 0 | PASS |
| invalid delivery chronology | 0 | PASS |
| unmapped promoted sale | 0 | PASS |

## Deliberate invalid inserts

| Case | Rejected |
|---|---|
| orphan order item | True |
| orphan sale | True |
| negative quantity | True |
| duplicate sales grain | True |
| duplicate inventory grain | True |
| invalid promotion range | True |
| invalid price | True |

Smoke queries executed: 10/10.
