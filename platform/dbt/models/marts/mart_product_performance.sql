select sku_id,sku_code,product_name,brand_name,category_name,count(distinct store_id) active_stores,
 sum(quantity_units) units_sold,sum(net_revenue) net_revenue,sum(gross_profit) gross_profit
from {{ ref('fact_sales') }} group by all

