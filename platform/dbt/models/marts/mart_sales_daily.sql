select sale_date,store_id,sku_id,brand_name,category_name,region_id,store_type,channel,
 sum(quantity_units) as units_sold,sum(net_revenue) as net_revenue,sum(gross_profit) as gross_profit,
 avg(transaction_unit_price) as average_transaction_price,sum(case when is_promo then quantity_units else 0 end) as promo_units
from {{ ref('fact_sales') }} group by all

