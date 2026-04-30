select d.*,p.product_name,p.brand_name,p.category_name,s.region_id,s.store_type,s.channel
from {{ ref('stg_daily_demand') }} d
join {{ ref('dim_product') }} p using(sku_id)
join {{ ref('dim_store') }} s using(store_id)
