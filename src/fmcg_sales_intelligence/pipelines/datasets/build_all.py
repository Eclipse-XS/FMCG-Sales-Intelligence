"""Build deterministic, point-in-time-safe ML/analytics Parquet datasets from DuckDB marts."""
from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
import json
import logging
from datetime import datetime,timezone
import duckdb
import polars as pl

ROOT = PROJECT_ROOT;DB=ROOT/"data/warehouse/fmcg.duckdb";OUT=ROOT/"data/processed";REPORTS=ROOT/"artifacts/reports/data_engineering"
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s");log=logging.getLogger(__name__)
def query(conn,sql):return pl.from_arrow(conn.execute(sql).arrow())
def save(name,frame,keys,date_col,target_cols=()):
    path=OUT/name/f"{name}_v1.parquet";path.parent.mkdir(parents=True,exist_ok=True);frame.write_parquet(path,compression="zstd")
    duplicate=frame.select(keys).is_duplicated().sum() if keys else 0
    meta={"dataset_name":name,"dataset_version":"v1","feature_version":"v1","generated_at":datetime.now(timezone.utc).isoformat(),"source_cutoff":str(frame[date_col].max()) if frame.height else None,"row_count":frame.height,"column_count":frame.width,"date_column":date_col,"date_range":[str(frame[date_col].min()),str(frame[date_col].max())] if frame.height else None,"keys":keys,"duplicate_keys":int(duplicate),"targets":list(target_cols),"schema":{c:str(t) for c,t in zip(frame.columns,frame.dtypes)}}
    path.with_suffix(".metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    REPORTS.mkdir(parents=True,exist_ok=True);(REPORTS/f"{name}.md").write_text("\n".join([f"# {name}","",f"- Grain keys: `{', '.join(keys)}`",f"- Rows: {frame.height}",f"- Columns: {frame.width}",f"- Date range: {meta['date_range']}",f"- Target columns: `{', '.join(target_cols) or 'none'}`",f"- Duplicate grain keys: {duplicate}",f"- Source cutoff: {meta['source_cutoff']}","", "The artifact is Parquet and metadata was generated with the same deterministic build."]),encoding="utf-8")
    log.info("wrote %s rows=%s cols=%s",name,frame.height,frame.width);return meta
def main():
    if not DB.exists():raise FileNotFoundError("Run extract_operational.py and dbt build first")
    metadata=[]
    with duckdb.connect(str(DB),read_only=True) as c:
        # Prediction is at the start of t.  The anchor grid is independent of
        # whether a sale happens on t; features use only history or schedules.
        forecasting=query(c,"""with anchors as (
          select observation_date prediction_date,store_id,sku_id,brand_name,category_name,region_id,store_type,channel
          from analytics.fact_daily_demand
        ), max_d as (select max(observation_date) max_date from analytics.fact_daily_demand)
        select a.prediction_date,a.store_id,a.sku_id,
          (select realized_sales_units from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date=a.prediction_date-interval 1 day) as lag_1,
          (select realized_sales_units from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date=a.prediction_date-interval 7 day) as lag_7,
          (select realized_sales_units from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date=a.prediction_date-interval 14 day) as lag_14,
          (select realized_sales_units from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date=a.prediction_date-interval 28 day) as lag_28,
          (select avg(realized_sales_units) from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date>=a.prediction_date-interval 7 day and x.observation_date<a.prediction_date) as rolling_mean_7d,
          (select stddev_samp(realized_sales_units) from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date>=a.prediction_date-interval 7 day and x.observation_date<a.prediction_date) as rolling_std_7d,
          (select sum(realized_sales_units) from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date>=a.prediction_date-interval 7 day and x.observation_date<a.prediction_date) as sales_velocity_7d,
          (select sum(case when demand_censored_by_inventory then 1 else 0 end) from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date>=a.prediction_date-interval 7 day and x.observation_date<a.prediction_date) as censored_days_prior_7d,
          pr.selling_price as scheduled_selling_price,
          (select min(p.promotion_id) from raw.promotions p join raw.promotion_stores ps using(promotion_id) join raw.promotion_skus pk using(promotion_id)
            where ps.store_id=a.store_id and pk.sku_id=a.sku_id and a.prediction_date between p.start_date and p.end_date) as scheduled_promotion_id,
          exists(select 1 from raw.promotions p join raw.promotion_stores ps using(promotion_id) join raw.promotion_skus pk using(promotion_id)
            where ps.store_id=a.store_id and pk.sku_id=a.sku_id and a.prediction_date between p.start_date and p.end_date) as scheduled_is_promo,
          a.brand_name,a.category_name,a.region_id,a.store_type,a.channel,
          (select count(distinct x.observation_date) from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date>a.prediction_date and x.observation_date<=a.prediction_date+interval 7 day) as target_observed_days_next_7d,
          (a.prediction_date+interval 7 day<=max_d.max_date and (select count(distinct x.observation_date) from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date>a.prediction_date and x.observation_date<=a.prediction_date+interval 7 day)=7) as target_observed_next_7d,
          case when a.prediction_date+interval 7 day<=max_d.max_date then (select sum(x.realized_sales_units) from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date>a.prediction_date and x.observation_date<=a.prediction_date+interval 7 day) end as target_units_next_7d,
          case when a.prediction_date+interval 7 day<=max_d.max_date then (select sum(x.requested_demand_units) from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date>a.prediction_date and x.observation_date<=a.prediction_date+interval 7 day) end as target_requested_demand_next_7d,
          case when a.prediction_date+interval 7 day<=max_d.max_date then (select sum(x.lost_sales_units) from analytics.fact_daily_demand x where x.store_id=a.store_id and x.sku_id=a.sku_id and x.observation_date>a.prediction_date and x.observation_date<=a.prediction_date+interval 7 day) end as target_lost_sales_next_7d
        from anchors a cross join max_d
        left join raw.product_prices pr on pr.store_id=a.store_id and pr.sku_id=a.sku_id and a.prediction_date between pr.valid_from and pr.valid_to
        """)
        metadata.append(save("forecasting",forecasting,["prediction_date","store_id","sku_id"],"prediction_date",["target_units_next_7d","target_requested_demand_next_7d","target_lost_sales_next_7d","target_observed_next_7d"]))
        stockout=query(c,"""with max_d as (select max(snapshot_date) max_date from analytics.fact_inventory)
        select i.snapshot_date as prediction_date,i.warehouse_id,i.sku_id,i.stock_quantity,i.reserved_quantity,i.available_quantity,i.reorder_point,i.safety_stock,
          i.available_quantity::double/nullif(i.safety_stock,0) as stock_to_safety_ratio,i.available_quantity-i.reorder_point as distance_to_reorder_point,
          (select avg(s.quantity_units) from analytics.fact_sales s where s.sku_id=i.sku_id and s.region_id=(select region_id from analytics.dim_warehouse w where w.warehouse_id=i.warehouse_id) and s.sale_date>=i.snapshot_date-interval 7 day and s.sale_date<i.snapshot_date) as sales_velocity_7d,
          (select sum(i2.replenishment_quantity) from analytics.fact_inventory i2 where i2.warehouse_id=i.warehouse_id and i2.sku_id=i.sku_id and i2.snapshot_date>=i.snapshot_date-interval 7 day and i2.snapshot_date<i.snapshot_date) as replenishment_sum_7d,
          (select min(future.snapshot_date) from analytics.fact_inventory future where future.warehouse_id=i.warehouse_id and future.sku_id=i.sku_id and future.snapshot_date>i.snapshot_date and future.snapshot_date<=i.snapshot_date+interval 7 day and future.available_quantity<=0) as first_stockout_date,
          exists(select 1 from analytics.fact_inventory future where future.warehouse_id=i.warehouse_id and future.sku_id=i.sku_id and future.snapshot_date>i.snapshot_date and future.snapshot_date<=i.snapshot_date+interval 7 day and future.available_quantity<=0) as stockout_within_7d,
          exists(select 1 from analytics.fact_inventory future where future.warehouse_id=i.warehouse_id and future.sku_id=i.sku_id and future.snapshot_date>i.snapshot_date and future.snapshot_date<=i.snapshot_date+interval 7 day and future.available_quantity<=0) as event_observed,
          date_diff('day',i.snapshot_date,(select min(future.snapshot_date) from analytics.fact_inventory future where future.warehouse_id=i.warehouse_id and future.sku_id=i.sku_id and future.snapshot_date>i.snapshot_date and future.snapshot_date<=i.snapshot_date+interval 7 day and future.available_quantity<=0)) as event_time_days,
          case when not exists(select 1 from analytics.fact_inventory future where future.warehouse_id=i.warehouse_id and future.sku_id=i.sku_id and future.snapshot_date>i.snapshot_date and future.snapshot_date<=i.snapshot_date+interval 7 day and future.available_quantity<=0)
            then least(7,greatest(0,date_diff('day',i.snapshot_date,max_d.max_date))) end as censor_time_days,
          i.snapshot_date+interval 7 day<=max_d.max_date as horizon_complete
        from analytics.fact_inventory i cross join max_d""")
        metadata.append(save("stockout",stockout,["prediction_date","warehouse_id","sku_id"],"prediction_date",["stockout_within_7d","event_observed","event_time_days","censor_time_days","horizon_complete"]))
        snapshots=query(c,"select distinct sale_date as snapshot_date from analytics.fact_sales where sale_date in ('2024-01-31','2024-02-29','2024-03-30')")
        c.register("snapshots",snapshots.to_arrow())
        store=query(c,"""select q.snapshot_date,s.store_id,s.region_id,s.store_type,s.channel,s.floor_area_m2,
          sum(f.net_revenue) revenue_30d,sum(f.quantity_units) units_30d,sum(f.gross_profit) profit_30d,count(distinct f.sku_id) active_skus_30d,
          avg(f.transaction_unit_price) average_price_30d,sum(case when f.is_promo then f.quantity_units else 0 end)::double/nullif(sum(f.quantity_units),0) promotion_unit_share_30d,
          stddev_samp(f.net_revenue) revenue_volatility_30d
        from snapshots q join analytics.dim_store s on true left join analytics.fact_sales f on f.store_id=s.store_id and f.sale_date>=q.snapshot_date-interval 30 day and f.sale_date<q.snapshot_date group by all""")
        metadata.append(save("segmentation",store,["snapshot_date","store_id"],"snapshot_date"))
        # Alias of the pre-clustering contract.  No cluster/target is published.
        metadata.append(save("segment_assignment",store,["snapshot_date","store_id"],"snapshot_date"))
        # Anomaly detection is explicitly post-event: current observed values
        # are available, while baselines remain historical.
        anomaly=query(c,"""select f.sale_date as event_date,f.store_id,f.sku_id,f.quantity_units as event_observed_units,
          f.transaction_unit_price as event_transaction_unit_price,f.is_promo as event_is_promo,
          l1.quantity_units as lag_1,l7.quantity_units as lag_7,avg(h.quantity_units) as rolling_mean_7d,stddev_samp(h.quantity_units) as rolling_std_7d,
          f.brand_name,f.category_name
        from analytics.fact_sales f
        left join analytics.fact_sales l1 on l1.store_id=f.store_id and l1.sku_id=f.sku_id and l1.sale_date=f.sale_date-interval 1 day
        left join analytics.fact_sales l7 on l7.store_id=f.store_id and l7.sku_id=f.sku_id and l7.sale_date=f.sale_date-interval 7 day
        left join analytics.fact_sales h on h.store_id=f.store_id and h.sku_id=f.sku_id and h.sale_date>=f.sale_date-interval 7 day and h.sale_date<f.sale_date
        group by all""")
        metadata.append(save("anomaly",anomaly,["event_date","store_id","sku_id"],"event_date"))
        basket=query(c,"""select order_id,order_date,store_id,sku_id,quantity,product_name,brand_name,category_name,region_id,store_type,channel from analytics.fact_order_items""")
        metadata.append(save("basket",basket,["order_id","sku_id"],"order_date"))
        promotion_daily=query(c,"""select * from analytics.mart_promotion_daily""")
        metadata.append(save("promotion_daily",promotion_daily,["promotion_id","store_id","sku_id","calendar_date"],"calendar_date"))
        promotion=query(c,"""select p.*,d.promotion_type,d.discount_type,d.discount_value from analytics.mart_promotion_performance p join analytics.dim_promotion d using(promotion_id)""")
        metadata.append(save("promotion_performance",promotion,["promotion_id","store_id","sku_id"],"start_date"))
    (REPORTS/"pipeline_validation.json").write_text(json.dumps({"built_at":datetime.now(timezone.utc).isoformat(),"datasets":metadata},indent=2),encoding="utf-8")
if __name__=="__main__":main()
