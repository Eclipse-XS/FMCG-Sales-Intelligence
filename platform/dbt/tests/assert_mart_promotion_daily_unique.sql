select promotion_id, store_id, sku_id, calendar_date
from {{ ref('mart_promotion_daily') }}
group by 1, 2, 3, 4
having count(*) > 1
