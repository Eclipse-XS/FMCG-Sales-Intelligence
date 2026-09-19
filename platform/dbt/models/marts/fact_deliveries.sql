select d.*,di.sku_id,di.quantity from {{ source('raw','deliveries') }} d join {{ source('raw','delivery_items') }} di using(delivery_id)

