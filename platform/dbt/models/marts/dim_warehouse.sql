select w.warehouse_id as warehouse_key,w.warehouse_id,w.warehouse_code,w.warehouse_name,w.region_id,r.region_name,w.city,w.capacity_units from {{ source('raw','warehouses') }} w join {{ source('raw','regions') }} r using(region_id)

