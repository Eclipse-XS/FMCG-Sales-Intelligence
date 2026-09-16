with grid as (
 select p.promotion_id,p.start_date,p.end_date,ps.store_id,pk.sku_id
 from {{ ref('dim_promotion') }} p join {{ source('raw','promotion_stores') }} ps using(promotion_id) join {{ source('raw','promotion_skus') }} pk using(promotion_id)
), sales as (select * from {{ ref('fact_sales') }})
select g.promotion_id,g.store_id,g.sku_id,g.start_date,g.end_date,
 sum(case when s.sale_date between g.start_date-30 and g.start_date-1 then s.quantity_units end) baseline_units,
 sum(case when s.sale_date between g.start_date and g.end_date then s.quantity_units end) promo_units,
 sum(case when s.sale_date between g.end_date+1 and g.end_date+30 then s.quantity_units end) post_units,
 sum(case when s.sale_date between g.start_date and g.end_date then s.net_revenue end) promo_revenue,
 sum(case when s.sale_date between g.start_date and g.end_date then s.gross_profit end) promo_profit
from grid g left join sales s on s.store_id=g.store_id and s.sku_id=g.sku_id and s.sale_date between g.start_date-30 and g.end_date+30
group by all

