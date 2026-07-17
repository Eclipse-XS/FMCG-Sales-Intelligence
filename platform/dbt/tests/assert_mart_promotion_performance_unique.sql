select promotion_id, store_id, sku_id
from {{ ref('mart_promotion_performance') }}
group by 1, 2, 3
having count(*) > 1
