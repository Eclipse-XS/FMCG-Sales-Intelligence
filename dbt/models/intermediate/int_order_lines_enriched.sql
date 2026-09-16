select o.order_id,o.order_date,o.store_id,oi.sku_id,oi.quantity,oi.unit_price,oi.discount_amount,oi.line_total,
 p.product_name,b.brand_name,c.category_name,s.region_id,s.store_type,s.channel
from {{ ref('stg_orders') }} o join {{ ref('stg_order_items') }} oi using(order_id)
join {{ source('raw','skus') }} k using(sku_id) join {{ source('raw','products') }} p using(product_id)
join {{ source('raw','brands') }} b using(brand_id) join {{ source('raw','categories') }} c using(category_id)
join {{ source('raw','stores') }} s using(store_id)

