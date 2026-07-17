select s.store_id as store_key,s.store_id,s.store_name,s.external_store_code,s.region_id,r.region_name,r.country,s.city,s.store_type,s.channel,s.floor_area_m2,s.opened_at
from {{ source('raw','stores') }} s join {{ source('raw','regions') }} r using(region_id)

