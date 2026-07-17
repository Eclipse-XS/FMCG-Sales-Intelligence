with sales as (select * from {{ ref('stg_sales') }}),
product as (select * from {{ source('raw','skus') }} k join {{ source('raw','products') }} p using(product_id) join {{ source('raw','brands') }} b using(brand_id) join {{ source('raw','categories') }} c using(category_id)),
store as (select s.*,r.region_name,r.country from {{ source('raw','stores') }} s join {{ source('raw','regions') }} r using(region_id)),
price as (select * from {{ source('raw','product_prices') }})
select s.sale_id,s.sale_date,s.store_id,s.sku_id,s.quantity_units,s.unit_price as transaction_unit_price,
 s.gross_revenue,s.discount_amount,s.net_revenue,s.unit_cost,s.gross_profit,s.promotion_id,
 p.sku_code,p.product_name,p.brand_name,p.category_name,p.package_type,p.volume_ml,
 st.region_id,st.region_name,st.store_type,st.channel,
 pr.regular_price,pr.selling_price as reference_selling_price,
 case when s.promotion_id is not null then true else false end as is_promo
from sales s join product p using(sku_id) join store st using(store_id)
left join price pr on pr.store_id=s.store_id and pr.sku_id=s.sku_id and s.sale_date between pr.valid_from and pr.valid_to

