select o.order_id,o.order_date,o.store_id,o.total_amount,o.discount_amount,count(oi.sku_id) as distinct_skus,
 sum(oi.quantity) as units,sum(oi.line_total) as line_total
from {{ ref('fact_orders') }} o join {{ ref('fact_order_items') }} oi using(order_id)
group by all

