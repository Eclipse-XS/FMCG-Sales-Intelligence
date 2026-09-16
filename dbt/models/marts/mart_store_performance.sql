select store_id,region_id,region_name,store_type,channel,count(distinct sale_date) active_days,count(distinct sku_id) active_skus,
 sum(quantity_units) units_sold,sum(net_revenue) net_revenue,sum(gross_profit) gross_profit,avg(transaction_unit_price) average_selling_price
from {{ ref('fact_sales') }} group by all

