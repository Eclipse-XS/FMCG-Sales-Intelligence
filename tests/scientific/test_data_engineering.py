from pathlib import Path

import duckdb
import polars as pl
from fmcg_sales_intelligence.pipelines.streaming.events import encode, sale_event, validate

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data/warehouse/fmcg.duckdb"


def data(name: str) -> pl.DataFrame:
    return pl.read_parquet(ROOT / f"data/processed/{name}/{name}_v1.parquet")


def sql(statement: str):
    with duckdb.connect(str(DB), read_only=True) as conn:
        return conn.execute(statement).fetchall()


def parquet(name: str) -> str:
    return (ROOT / f"data/processed/{name}/{name}_v1.parquet").as_posix()


def test_every_published_dataset_has_unique_contract_grain():
    specs = {
        "forecasting": ["prediction_date", "store_id", "sku_id"],
        "stockout": ["prediction_date", "warehouse_id", "sku_id"],
        "segmentation": ["snapshot_date", "store_id"],
        "segment_assignment": ["snapshot_date", "store_id"],
        "anomaly": ["event_date", "store_id", "sku_id"],
        "basket": ["order_id", "sku_id"],
        "promotion_performance": ["promotion_id", "store_id", "sku_id"],
    }
    for name, keys in specs.items():
        assert data(name).select(keys).is_duplicated().sum() == 0, name


def test_forecasting_lags_are_exact_historical_dates():
    path = parquet("forecasting")
    for days in (1, 7, 14, 28):
        mismatch = sql(f"""select count(*) from read_parquet('{path}') f
          left join analytics.fact_daily_demand s on s.store_id=f.store_id and s.sku_id=f.sku_id
           and s.observation_date=f.prediction_date-interval {days} day
          where f.lag_{days} is distinct from s.realized_sales_units""")[0][0]
        assert mismatch == 0


def test_forecasting_rolling_window_is_strictly_t_minus_7_to_t():
    path = parquet("forecasting")
    mismatch = sql(f"""select count(*) from read_parquet('{path}') f where
      coalesce(abs(f.rolling_mean_7d-(select avg(s.realized_sales_units) from analytics.fact_daily_demand s where s.store_id=f.store_id and s.sku_id=f.sku_id and s.observation_date>=f.prediction_date-interval 7 day and s.observation_date<f.prediction_date)),0)>1e-9
      or (f.rolling_mean_7d is null) <> ((select avg(s.realized_sales_units) from analytics.fact_daily_demand s where s.store_id=f.store_id and s.sku_id=f.sku_id and s.observation_date>=f.prediction_date-interval 7 day and s.observation_date<f.prediction_date) is null)
      or coalesce(abs(f.rolling_std_7d-(select stddev_samp(s.realized_sales_units) from analytics.fact_daily_demand s where s.store_id=f.store_id and s.sku_id=f.sku_id and s.observation_date>=f.prediction_date-interval 7 day and s.observation_date<f.prediction_date)),0)>1e-9
      or (f.rolling_std_7d is null) <> ((select stddev_samp(s.realized_sales_units) from analytics.fact_daily_demand s where s.store_id=f.store_id and s.sku_id=f.sku_id and s.observation_date>=f.prediction_date-interval 7 day and s.observation_date<f.prediction_date) is null)
      or f.sales_velocity_7d is distinct from (select sum(s.realized_sales_units) from analytics.fact_daily_demand s where s.store_id=f.store_id and s.sku_id=f.sku_id and s.observation_date>=f.prediction_date-interval 7 day and s.observation_date<f.prediction_date)""")[0][0]
    assert mismatch == 0


def test_forecasting_target_is_sum_over_open_closed_next_7_day_window():
    path = parquet("forecasting")
    mismatch = sql(f"""with max_d as (select max(observation_date) d from analytics.fact_daily_demand)
      select count(*) from read_parquet('{path}') f cross join max_d where
      f.target_observed_days_next_7d is distinct from (select count(distinct s.observation_date) from analytics.fact_daily_demand s where s.store_id=f.store_id and s.sku_id=f.sku_id and s.observation_date>f.prediction_date and s.observation_date<=f.prediction_date+interval 7 day)
      or f.target_observed_next_7d is distinct from (f.prediction_date+interval 7 day<=max_d.d)
      or f.target_units_next_7d is distinct from case when f.prediction_date+interval 7 day<=max_d.d then (select sum(s.realized_sales_units) from analytics.fact_daily_demand s where s.store_id=f.store_id and s.sku_id=f.sku_id and s.observation_date>f.prediction_date and s.observation_date<=f.prediction_date+interval 7 day) end
      or f.target_requested_demand_next_7d is distinct from case when f.prediction_date+interval 7 day<=max_d.d then (select sum(s.requested_demand_units) from analytics.fact_daily_demand s where s.store_id=f.store_id and s.sku_id=f.sku_id and s.observation_date>f.prediction_date and s.observation_date<=f.prediction_date+interval 7 day) end""")[0][0]
    assert mismatch == 0


def test_forecasting_contract_has_no_same_day_realized_leakage():
    columns = set(data("forecasting").columns)
    forbidden = {"observed_units", "transaction_unit_price", "is_promo", "target_units_7d", "target_observed_7d"}
    assert not columns.intersection(forbidden)
    assert {"scheduled_selling_price", "scheduled_promotion_id", "scheduled_is_promo"}.issubset(columns)


def test_complete_grid_zero_sales_and_unavailable_history_are_distinct():
    f = data("forecasting")
    demand_rows = sql("select count(*) from analytics.fact_daily_demand")[0][0]
    assert f.height == demand_rows
    assert f.filter((pl.col("prediction_date") == pl.col("prediction_date").min()) & pl.col("lag_1").is_not_null()).height == 0
    assert f.filter((pl.col("prediction_date") > pl.col("prediction_date").min()) & (pl.col("lag_1") == 0)).height > 0


def test_requested_realized_lost_demand_reconciles():
    mismatch = sql("""select count(*) from analytics.fact_daily_demand where requested_demand_units<>realized_sales_units+lost_sales_units or demand_censored_by_inventory<>(lost_sales_units>0)""")[0][0]
    assert mismatch == 0


def test_stockout_first_event_and_open_closed_interval():
    path = parquet("stockout")
    mismatch = sql(f"""select count(*) from read_parquet('{path}') f where
      f.first_stockout_date is distinct from (select min(i.snapshot_date) from analytics.fact_inventory i where i.warehouse_id=f.warehouse_id and i.sku_id=f.sku_id and i.snapshot_date>f.prediction_date and i.snapshot_date<=f.prediction_date+interval 7 day and i.available_quantity<=0)
      or f.stockout_within_7d is distinct from exists(select 1 from analytics.fact_inventory i where i.warehouse_id=f.warehouse_id and i.sku_id=f.sku_id and i.snapshot_date>f.prediction_date and i.snapshot_date<=f.prediction_date+interval 7 day and i.available_quantity<=0)""")[0][0]
    assert mismatch == 0


def test_stockout_censoring_semantics():
    path = parquet("stockout")
    mismatch = sql(f"""with max_d as (select max(snapshot_date) d from analytics.fact_inventory)
      select count(*) from read_parquet('{path}') f cross join max_d where
      f.event_observed is distinct from f.stockout_within_7d
      or f.event_time_days is distinct from case when f.event_observed then date_diff('day',f.prediction_date,f.first_stockout_date) end
      or f.censor_time_days is distinct from case when not f.event_observed then least(7,greatest(0,date_diff('day',f.prediction_date,max_d.d))) end
      or f.horizon_complete is distinct from (f.prediction_date+interval 7 day<=max_d.d)
      or (f.event_observed and f.censor_time_days is not null)
      or (not f.event_observed and f.event_time_days is not null)""")[0][0]
    assert mismatch == 0


def test_segmentation_uses_strict_pre_snapshot_30_day_window():
    path = parquet("segmentation")
    mismatch = sql(f"""select count(*) from read_parquet('{path}') f where
      f.revenue_30d is distinct from (select sum(s.net_revenue) from analytics.fact_sales s where s.store_id=f.store_id and s.sale_date>=f.snapshot_date-interval 30 day and s.sale_date<f.snapshot_date)
      or f.units_30d is distinct from (select sum(s.quantity_units) from analytics.fact_sales s where s.store_id=f.store_id and s.sale_date>=f.snapshot_date-interval 30 day and s.sale_date<f.snapshot_date)
      or f.active_skus_30d is distinct from (select count(distinct s.sku_id) from analytics.fact_sales s where s.store_id=f.store_id and s.sale_date>=f.snapshot_date-interval 30 day and s.sale_date<f.snapshot_date)""")[0][0]
    assert mismatch == 0


def test_segment_assignment_is_only_an_alias_without_labels():
    segment = data("segmentation")
    alias = data("segment_assignment")
    assert alias.columns == segment.columns
    assert alias.equals(segment)
    assert "cluster_id" not in alias.columns and "target_origin" not in alias.columns


def test_anomaly_contract_is_post_event_and_has_no_supervised_label():
    columns = set(data("anomaly").columns)
    assert {"event_observed_units", "event_transaction_unit_price", "event_is_promo"}.issubset(columns)
    assert not {"anomaly_label", "is_anomaly", "forecast_residual"}.intersection(columns)


def test_basket_order_sku_integrity():
    path = parquet("basket")
    duplicate = sql(f"select count(*) from (select order_id,sku_id,count(*) n from read_parquet('{path}') group by 1,2 having n>1)")[0][0]
    orphan = sql(f"""select count(*) from read_parquet('{path}') b left join raw.orders o using(order_id) left join raw.skus s using(sku_id) where o.order_id is null or s.sku_id is null""")[0][0]
    assert duplicate == 0 and orphan == 0


def test_promotion_grid_is_unique_and_has_no_overlap_or_sales_fanout():
    duplicate = sql("""select count(*) from (select promotion_id,store_id,sku_id,count(*) n from analytics.mart_promotion_performance group by 1,2,3 having n>1)""")[0][0]
    overlap = sql("""select count(*) from analytics.mart_promotion_performance a join analytics.mart_promotion_performance b on a.promotion_id<b.promotion_id and a.store_id=b.store_id and a.sku_id=b.sku_id and a.start_date<=b.end_date and b.start_date<=a.end_date""")[0][0]
    fanout = sql("""with x as (select s.sale_id,count(*) n from analytics.fact_sales s join analytics.mart_promotion_performance p on p.store_id=s.store_id and p.sku_id=s.sku_id and s.sale_date between p.start_date and p.end_date group by 1) select count(*) from x where n>1""")[0][0]
    assert duplicate == 0 and overlap == 0 and fanout == 0


def test_kafka_envelope_validation():
    event = sale_event({"sale_id": 1, "sale_date": "2024-01-01", "store_id": 1, "sku_id": 1, "quantity_units": 2, "unit_price": 1.5})
    assert validate(encode(event))["event_type"] == "sale"
    try:
        validate(b'{"bad":true}')
    except ValueError:
        pass
    else:
        raise AssertionError("malformed event accepted")
