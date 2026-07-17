select k.sku_id,k.sku_code,k.product_id,p.product_name,p.category_id,c.category_name,p.brand_id,b.brand_name,
       k.package_type,k.volume_ml,k.base_price,k.standard_cost,p.sugar_free,
       s.store_id,s.store_name,s.region_id,r.region_name,r.country,s.city,s.store_type,s.channel,s.floor_area_m2
from {{ source('raw','skus') }} k
join {{ source('raw','products') }} p using(product_id)
join {{ source('raw','categories') }} c using(category_id)
join {{ source('raw','brands') }} b using(brand_id)
cross join {{ source('raw','stores') }} s
join {{ source('raw','regions') }} r using(region_id)
