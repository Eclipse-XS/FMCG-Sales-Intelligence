-- 1 Daily sales by SKU
SELECT sale_date, sku_id, sum(quantity_units) units FROM fmcg.sales GROUP BY sale_date, sku_id ORDER BY sale_date, sku_id LIMIT 20;
-- 2 Sales by brand and category
SELECT b.brand_name,c.category_name,sum(s.net_revenue) revenue FROM fmcg.sales s JOIN fmcg.skus k USING(sku_id) JOIN fmcg.products p USING(product_id) JOIN fmcg.brands b USING(brand_id) JOIN fmcg.categories c USING(category_id) GROUP BY 1,2 ORDER BY revenue DESC;
-- 3 Sales by region/store
SELECT r.region_name,st.store_name,sum(s.net_revenue) revenue FROM fmcg.sales s JOIN fmcg.stores st USING(store_id) JOIN fmcg.regions r USING(region_id) GROUP BY 1,2 ORDER BY revenue DESC LIMIT 20;
-- 4 Top SKUs
SELECT sku_id,sum(net_revenue) revenue FROM fmcg.sales GROUP BY sku_id ORDER BY revenue DESC LIMIT 10;
-- 5 Promotion comparison
SELECT promotion_id IS NOT NULL promoted,sum(quantity_units) units,avg(unit_price) avg_price FROM fmcg.sales GROUP BY 1;
-- 6 Price history
SELECT * FROM fmcg.product_prices WHERE store_id=1 AND sku_id=1 ORDER BY valid_from;
-- 7 Inventory history
SELECT * FROM fmcg.inventory WHERE warehouse_id=1 AND sku_id=1 ORDER BY snapshot_date;
-- 8 Basket contents
SELECT o.order_code,oi.sku_id,oi.quantity,oi.line_total FROM fmcg.orders o JOIN fmcg.order_items oi USING(order_id) WHERE o.order_id=1 ORDER BY oi.order_item_id;
-- 9 Average basket size
SELECT avg(lines) average_distinct_skus FROM (SELECT order_id,count(*) lines FROM fmcg.order_items GROUP BY order_id) x;
-- 10 Low stock
SELECT snapshot_date,warehouse_id,sku_id,available_quantity,reorder_point FROM fmcg.inventory WHERE available_quantity<=reorder_point ORDER BY snapshot_date DESC LIMIT 20;

