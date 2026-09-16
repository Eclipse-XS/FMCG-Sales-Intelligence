from __future__ import annotations
from datetime import date,timedelta
from pathlib import Path
import sys
import polars as pl
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
CONFIG=ROOT/"configs/modeling"

def read(name):return yaml.safe_load((CONFIG/f"{name}.yaml").read_text(encoding="utf-8"))
def dataset(name):return pl.read_parquet(next((ROOT/"data/processed"/name).glob("*.parquet")))
def as_date(value):return value if isinstance(value,date) else date.fromisoformat(value)

def test_all_modeling_contracts_parse_and_have_status():
    names=["forecasting","stockout_classification","stockout_survival","segmentation","anomaly","basket","promotion"]
    for name in names:
        contract=read(name)
        assert contract["contract_version"]==1
        assert contract["task"]
        assert contract.get("status") in {"READY","READY_WITH_LIMITATIONS"}

def test_forecasting_feature_and_target_contract_matches_dataset():
    c=read("forecasting");f=dataset("forecasting")
    allowed={x for values in c["features"].values() for x in values}
    assert allowed.issubset(f.columns)
    assert c["primary_target"] in f.columns
    assert c["primary_target"] not in allowed
    assert not allowed.intersection(c["forbidden_features"])
    assert not {"store_id","sku_id","region_id"}.intersection(c["features"]["numerical_continuous"]+c["features"]["numerical_count"])

def test_forecasting_temporal_splits_are_ordered_purged_and_match_counts():
    c=read("forecasting");f=dataset("forecasting");s=c["split"]
    assert as_date(s["selection_train"]["end"])+timedelta(days=s["embargo_days"])<as_date(s["validation"]["start"])
    assert as_date(s["final_train"]["end"])+timedelta(days=s["embargo_days"])<as_date(s["test"]["start"])
    for name in ("selection_train","validation","final_train","test"):
        block=s[name];actual=f.filter((pl.col("prediction_date")>=as_date(block["start"]))&(pl.col("prediction_date")<=as_date(block["end"]))&pl.col("target_observed_next_7d")).height
        assert actual==block["rows"]

def test_stockout_contract_excludes_future_outcomes_and_split_has_events():
    c=read("stockout_classification");f=dataset("stockout");allowed={x for values in c["features"].values() for x in values}
    assert allowed.issubset(f.columns) and not allowed.intersection(c["forbidden_features"])
    assert not {"warehouse_id","sku_id"}.intersection(c["features"]["numerical_count"]+c["features"]["numerical_continuous"])
    for name in ("selection_train","validation","final_train","test"):
        block=c["split"][name];x=f.filter((pl.col("prediction_date")>=as_date(block["start"]))&(pl.col("prediction_date")<=as_date(block["end"]))&(pl.col("event_observed")|pl.col("horizon_complete")))
        assert x.height==block["rows"]
        assert x.filter(pl.col("event_observed")).height==block["positive_horizons"]>0
        assert block["episode_starts"]>0

def test_segmentation_uses_one_independent_latest_snapshot():
    c=read("segmentation");f=dataset("segmentation");latest=as_date(c["primary_snapshot"])
    assert f.filter(pl.col("snapshot_date")==latest).height==20
    assert f["store_id"].n_unique()==20 and f["snapshot_date"].n_unique()==3

def test_non_supervised_contracts_do_not_fabricate_targets():
    anomaly=read("anomaly");basket=read("basket");promotion=read("promotion")
    assert "anomaly_label" in anomaly["forbidden_features"]
    assert basket["transaction_id"]=="order_id"
    assert "causal_uplift" in promotion["forbidden_claims"]
