from __future__ import annotations
from pathlib import Path
from typing import Any
import polars as pl
from .config import EDAConfig
from .errors import RequiredColumnsError
from .models import Finding, Readiness, Severity
from .profiling import profile

KEYS = {
 "forecasting":["prediction_date","store_id","sku_id"], "stockout":["prediction_date","warehouse_id","sku_id"],
 "segmentation":["snapshot_date","store_id"], "anomaly":["event_date","store_id","sku_id"],
 "basket":["order_id","sku_id"], "promotion":["promotion_id","store_id","sku_id"]}
DATES = {"forecasting":"prediction_date","stockout":"prediction_date","segmentation":"snapshot_date","anomaly":"event_date","basket":"order_date","promotion":"start_date"}

def require(frame: pl.DataFrame, columns: set[str], task: str) -> None:
    missing = columns-set(frame.columns)
    if missing: raise RequiredColumnsError(f"{task} requires columns: {sorted(missing)}")

def _episodes(inventory: pl.DataFrame) -> pl.DataFrame:
    from fmcg_sales_intelligence.pipelines.refinement.episodes import stockout_episodes
    return stockout_episodes(inventory)

def analyze(task: str, frame: pl.DataFrame, path: Path, config: EDAConfig) -> tuple[dict[str,Any],dict[str,Any],list[Finding],dict[str,Readiness]]:
    generic = profile(frame, KEYS[task], DATES[task], config.top_n)
    function = globals()[f"analyze_{task}"]
    metrics, findings, readiness = function(frame, path, config)
    return metrics, generic, findings, readiness

def analyze_forecasting(f: pl.DataFrame, path: Path, config: EDAConfig):
    require(f,{"target_observed_next_7d","target_units_next_7d","target_requested_demand_next_7d","target_lost_sales_next_7d","prediction_date","store_id","sku_id"},"forecasting")
    complete=f.filter(pl.col("target_observed_next_7d")); total=f.height
    demand_path=config.warehouse_root/"raw"/"daily_demand.parquet"
    if path.resolve()==config.default_paths["forecasting"].resolve() and demand_path.exists():
        d=pl.read_parquet(demand_path); positive=d.filter(pl.col("realized_sales_units")>0).height; censored=d.filter(pl.col("demand_censored_by_inventory")).height
        requested=int(d["requested_demand_units"].sum());realized=int(d["realized_sales_units"].sum());lost=int(d["lost_sales_units"].sum())
        intermittent=d.group_by(["store_id","sku_id"]).agg((pl.col("realized_sales_units")==0).mean().alias("zero_rate"))
        temporal=d.group_by("observation_date").agg(pl.col("realized_sales_units").sum().alias("units"),pl.col("lost_sales_units").sum().alias("lost_units")).sort("observation_date").to_dicts()
    else:
        positive=None;censored=None;requested=int(complete["target_requested_demand_next_7d"].sum()) if complete.height else 0;realized=int(complete["target_units_next_7d"].sum()) if complete.height else 0;lost=int(complete["target_lost_sales_next_7d"].sum()) if complete.height else 0;intermittent=None;temporal=[]
    coverage=complete.height/total if total else 0
    end_incomplete=f.filter(~pl.col("target_observed_next_7d")).height
    early_nulls={c:f[c].null_count() for c in ("lag_1","lag_7","lag_14","lag_28","rolling_mean_7d") if c in f.columns}
    metrics={"prediction_rows":total,"complete_target_rows":complete.height,"target_coverage":coverage,"target_incomplete_rows":end_incomplete,
      "positive_sales_rows":positive,"zero_sales_rows":total-positive if positive is not None else None,"zero_sales_rate":(total-positive)/total if positive is not None and total else None,
      "inventory_censored_rows":censored,"inventory_censored_rate":censored/total if censored is not None and total else None,
      "requested_units":requested,"realized_units":realized,"lost_units":lost,
      "target_distribution":profile(complete.select("target_units_next_7d"))["numeric"]["target_units_next_7d"],
      "structural_history_nulls":early_nulls,"series_count":f.select(["store_id","sku_id"]).unique().height,
      "intermittent_zero_rate":profile(intermittent.select("zero_rate"))["numeric"]["zero_rate"] if intermittent is not None else None,
      "temporal_sales":temporal,
      "target_variation":{"store":complete.group_by("store_id").agg(pl.col("target_units_next_7d").mean().alias("mean_target")).to_dicts(),"sku":complete.group_by("sku_id").agg(pl.col("target_units_next_7d").mean().alias("mean_target")).to_dicts(),"category":complete.group_by("category_name").agg(pl.col("target_units_next_7d").mean().alias("mean_target")).to_dicts(),"channel":complete.group_by("channel").agg(pl.col("target_units_next_7d").mean().alias("mean_target")).to_dicts()},
      "price_summary":profile(f.select("scheduled_selling_price"))["numeric"]["scheduled_selling_price"],
      "lag_rolling_summary":profile(f.select([c for c in ["lag_1","lag_7","lag_14","lag_28","rolling_mean_7d","rolling_std_7d","sales_velocity_7d"] if c in f.columns]))["numeric"],
      "scheduled_promotion_rate":float(f["scheduled_is_promo"].mean()) if "scheduled_is_promo" in f.columns else None}
    if coverage<config.target_coverage_critical: ready=Readiness.NOT_READY
    elif coverage<config.target_coverage_warning: ready=Readiness.READY_WITH_LIMITATIONS
    else: ready=Readiness.READY_WITH_LIMITATIONS if f["prediction_date"].n_unique()<365 else Readiness.READY
    findings=[Finding("FORECAST_TARGET_COVERAGE",Severity.INFO,"Share of rows with a complete (t,t+7] target.",coverage),
      Finding("FORECAST_SHORT_HISTORY",Severity.WARNING,"History is shorter than one annual cycle.",f["prediction_date"].n_unique(),"Use rolling-origin validation and avoid seasonal claims beyond observed history.")]
    return metrics,findings,{"forecasting":ready}

def analyze_stockout(f: pl.DataFrame,path:Path,config:EDAConfig):
    require(f,{"event_observed","horizon_complete","event_time_days","available_quantity","warehouse_id","sku_id","prediction_date"},"stockout")
    events=f.filter(pl.col("event_observed")); complete_non=f.filter((~pl.col("event_observed"))&pl.col("horizon_complete")); incomplete_non=f.filter((~pl.col("event_observed"))&(~pl.col("horizon_complete")))
    inv_path=config.warehouse_root/"raw"/"inventory.parquet"
    episodes=_episodes(pl.read_parquet(inv_path)) if path.resolve()==config.default_paths["stockout"].resolve() and inv_path.exists() else pl.DataFrame()
    ec=episodes.height; known=events.height+complete_non.height
    metrics={"rows":f.height,"positive_horizons":events.height,"complete_non_events":complete_non.height,"incomplete_non_events":incomplete_non.height,
      "event_rate":events.height/known if known else 0,"censoring_rate":incomplete_non.height/f.height if f.height else 0,"independent_episodes":ec,
      "affected_series":episodes.select(["warehouse_id","sku_id"]).unique().height if ec else None,
      "episode_duration":profile(episodes.select("duration_days"))["numeric"].get("duration_days") if ec else None,
      "episodes_by_warehouse":episodes.group_by("warehouse_id").len().sort("warehouse_id").to_dicts() if ec else [],
      "episodes_by_sku":episodes.group_by("sku_id").len().sort("len",descending=True).to_dicts() if ec else [],
      "episodes_by_date":episodes.group_by("episode_start").len().sort("episode_start").to_dicts() if ec else [],
      "event_features":profile(events.select([c for c in ["available_quantity","stock_to_safety_ratio","distance_to_reorder_point","sales_velocity_7d","replenishment_sum_7d"] if c in f.columns]))["numeric"],
      "complete_non_event_features":profile(complete_non.select([c for c in ["available_quantity","stock_to_safety_ratio","distance_to_reorder_point","sales_velocity_7d","replenishment_sum_7d"] if c in f.columns]))["numeric"]}
    ready=Readiness.NOT_READY if ec<config.stockout_episode_warning else Readiness.READY_WITH_LIMITATIONS
    findings=[Finding("STOCKOUT_EPISODE_COUNT",Severity.WARNING if ready!=Readiness.READY else Severity.INFO,"Independent physical stockout episodes.",ec,"Use episode-aware temporal evaluation.")]
    return metrics,findings,{"stockout_classification":ready,"stockout_survival":ready}

def analyze_segmentation(f,path,config):
    require(f,{"snapshot_date","store_id","revenue_30d","units_30d"},"segmentation")
    features=[c for c in f.columns if c.endswith("_30d")]
    corr=f.select(features).corr().to_dicts() if features else []
    stability=f.sort(["store_id","snapshot_date"]).group_by("store_id").agg([pl.col(c).std().alias(c) for c in features]).to_dicts()
    outliers={}
    for c in features:
        s=f[c].cast(pl.Float64);q1=float(s.quantile(.25));q3=float(s.quantile(.75));iqr=q3-q1
        outliers[c]=int(((s<q1-1.5*iqr)|(s>q3+1.5*iqr)).sum())
    metrics={"rows":f.height,"stores":f["store_id"].n_unique(),"snapshots":f["snapshot_date"].n_unique(),"feature_summaries":profile(f.select(features))["numeric"],"correlations":corr,"snapshot_stability":stability,"outlier_candidates_iqr":outliers}
    return metrics,[Finding("SEGMENT_STORE_COUNT",Severity.WARNING,"Only a small number of independent stores is available.",metrics["stores"])],{"segmentation":Readiness.READY_WITH_LIMITATIONS}

def analyze_anomaly(f,path,config):
    require(f,{"event_observed_units","rolling_mean_7d","rolling_std_7d"},"anomaly")
    x=f.with_columns(((pl.col("event_observed_units")-pl.col("rolling_mean_7d"))/pl.col("rolling_std_7d")).alias("historical_z"))
    candidates=x.filter(pl.col("historical_z").abs()>=3).height
    return {"rows":f.height,"absolute_z_ge_3_candidates":candidates,"observed_units":profile(f.select("event_observed_units"))["numeric"]["event_observed_units"],"historical_deviation":profile(x.select("historical_z"))["numeric"]["historical_z"],"volatility_by_sku":x.group_by("sku_id").agg(pl.col("event_observed_units").std().alias("units_std")).sort("units_std",descending=True).head(config.top_n).to_dicts()},[Finding("ANOMALY_UNVERIFIED_CANDIDATES",Severity.INFO,"Candidates are contextual deviations, not labels.",candidates)],{"anomaly":Readiness.READY_WITH_LIMITATIONS}

def analyze_basket(f,path,config):
    require(f,{"order_id","sku_id","quantity"},"basket")
    sizes=f.group_by("order_id").agg(pl.col("quantity").sum().alias("basket_units"),pl.len().alias("distinct_lines"))
    top=f.group_by("sku_id").agg(pl.col("order_id").n_unique().alias("orders")).sort("orders",descending=True).head(config.top_n)
    pairs=(f.select(["order_id","sku_id"]).join(f.select(["order_id",pl.col("sku_id").alias("sku_b")]),on="order_id").filter(pl.col("sku_id")<pl.col("sku_b")).group_by(["sku_id","sku_b"]).len().sort("len",descending=True).head(config.top_n))
    return {"rows":f.height,"orders":f["order_id"].n_unique(),"skus":f["sku_id"].n_unique(),"basket_size":profile(sizes)["numeric"],"top_skus":top.to_dicts(),"top_brands":f.group_by("brand_name").agg(pl.col("order_id").n_unique().alias("orders")).sort("orders",descending=True).to_dicts(),"top_categories":f.group_by("category_name").agg(pl.col("order_id").n_unique().alias("orders")).sort("orders",descending=True).to_dicts(),"top_cooccurrences":pairs.to_dicts()},[Finding("BASKET_VALID_LONG_FORMAT",Severity.INFO,"Order-SKU representation is suitable for descriptive association analysis.")],{"basket":Readiness.READY}

def analyze_promotion(f,path,config):
    require(f,{"promotion_id","store_id","sku_id","baseline_units","promo_units","post_units"},"promotion")
    baseline_null=f["baseline_units"].null_count();post_null=f["post_units"].null_count()
    metrics={"rows":f.height,"promotions":f["promotion_id"].n_unique(),"baseline_null_rows":baseline_null,"post_null_rows":post_null,
      "promo_units":profile(f.select("promo_units"))["numeric"]["promo_units"],
      "descriptive_uplift_mean":float(f.select(((pl.col("promo_units")-pl.col("baseline_units"))/pl.col("baseline_units").replace(0,None)).mean()).item()) if f.filter(pl.col("baseline_units")>0).height else None,
      "by_promotion":f.group_by("promotion_id").agg(pl.col("baseline_units").sum(),pl.col("promo_units").sum(),pl.col("post_units").sum()).to_dicts(),
      "by_store_type":f.group_by("store_type").agg(pl.col("promo_units").mean().alias("mean_promo_units")).to_dicts(),"by_region":f.group_by("region_id").agg(pl.col("promo_units").mean().alias("mean_promo_units")).to_dicts()}
    return metrics,[Finding("PROMOTION_NON_CAUSAL",Severity.WARNING,"Before/during/after uplift is descriptive and must not be interpreted causally.")],{"promotion":Readiness.READY_WITH_LIMITATIONS}
