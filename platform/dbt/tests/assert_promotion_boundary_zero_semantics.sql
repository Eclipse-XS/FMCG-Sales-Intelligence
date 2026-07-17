select *
from {{ ref('mart_promotion_daily') }}
where
    (is_observable and realized_sales_units is null)
    or (not is_observable and realized_sales_units is not null)
    or (is_observable and valid_selling_price is null)
