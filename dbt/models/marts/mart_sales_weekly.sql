select date_trunc('week',sale_date)::date as week_start,store_id,sku_id,brand_name,category_name,
 sum(quantity_units) as units_sold,sum(net_revenue) as net_revenue,sum(gross_profit) as gross_profit
from {{ ref('fact_sales') }} group by all

