select i.snapshot_date,i.warehouse_id,i.sku_id,i.stock_quantity,i.reserved_quantity,i.available_quantity,i.reorder_point,i.safety_stock,
 i.replenishment_quantity,i.demand_fulfilled,i.adjustment_quantity,w.region_id,w.region_name
from {{ ref('fact_inventory') }} i join {{ ref('dim_warehouse') }} w using(warehouse_id)

