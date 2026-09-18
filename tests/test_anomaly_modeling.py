from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.modeling import run_experiment
from src.modeling.anomaly import (DEFAULT_CONFIG, agreement,
                                  canonical_iforest_score, detect_runs,
                                  fit_iforest, load_data,
                                  recompute_historical_stats,
                                  score_z_baseline, temporal_masks)

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/processed/anomaly/anomaly_v1.parquet"

def test_dataset_grain_and_no_ground_truth():
    _,d=load_data(); assert len(d)==35032
    assert not d[["event_date","store_id","sku_id"]].duplicated().any()
    assert not {"anomaly_label","is_anomaly","forecast_residual"}&set(d.columns)

def test_historical_window_excludes_current_and_future():
    d=pd.DataFrame({"event_date":pd.to_datetime(["2024-01-01","2024-01-02","2024-01-03","2024-01-04"]),"store_id":[1]*4,"sku_id":[1]*4,"event_observed_units":[1,3,100,5]})
    x=recompute_historical_stats(d,7)
    assert np.isnan(x.loc[0,"historical_mean_7d"])
    assert x.loc[1,"historical_mean_7d"]==1
    assert x.loc[2,"historical_mean_7d"]==2
    changed=d.copy(); changed.loc[3,"event_observed_units"]=9999
    assert recompute_historical_stats(changed,7).loc[2,"historical_mean_7d"]==2

def test_insufficient_history_zero_variance_and_direction():
    cfg,_=load_data(); d=pd.DataFrame({"event_date":pd.date_range("2024-01-01",periods=4),"store_id":[1]*4,"sku_id":[1]*4,"event_observed_units":[2,2,2,9]})
    x=score_z_baseline(d,cfg)
    assert not x.loc[0,"zscore_scorable"] and not x.loc[1,"zscore_scorable"]
    assert x.loc[2,"historical_zscore"]==0 and x.loc[2,"zscore_direction"]=="NONE"
    assert np.isposinf(x.loc[3,"historical_zscore"]) and x.loc[3,"zscore_direction"]=="HIGH" and x.loc[3,"zscore_candidate"]

def test_feature_contract_and_temporal_boundary():
    cfg,d=load_data(); ref,score=temporal_masks(d,cfg)
    assert not set(cfg["features"])&set(cfg["identifiers"]+cfg["context_only"]+cfg["forbidden_features"])
    assert d.loc[ref,"event_date"].max()<d.loc[score,"event_date"].min()

def test_iforest_reference_fit_orientation_and_determinism():
    cfg,d=load_data(); ref,score=temporal_masks(d,cfg); p1,m1=fit_iforest(d[ref],cfg); p2,m2=fit_iforest(d[ref],cfg)
    s1=canonical_iforest_score(p1,m1,d[score].head(100),cfg["features"]); s2=canonical_iforest_score(p2,m2,d[score].head(100),cfg["features"])
    assert np.allclose(s1,s2)
    raw=m1.decision_function(p1.transform(d[score].head(100)[cfg["features"]]))
    assert np.allclose(s1,-raw)

def test_agreement_and_run_detection():
    d=pd.DataFrame({"event_date":pd.to_datetime(["2024-01-01","2024-01-02","2024-01-04"]),"store_id":[1]*3,"sku_id":[1]*3,"zscore_candidate":[1,1,0],"iforest_candidate":[1,0,1]})
    a=agreement(d); assert a["both_flagged_count"]==1 and a["union_count"]==3 and a["jaccard_agreement"]==1/3
    r=detect_runs(d,"zscore_candidate","ZSCORE"); assert len(r)==1 and r.iloc[0].run_length==2

def test_public_api_artifacts_review_and_reload(tmp_path):
    result=run_experiment("anomaly",output_dir=tmp_path/"anomaly",experiment_id="test_anomaly",overwrite=True); out=Path(result["output_dir"])
    scores=pd.read_parquet(out/"predictions_or_scores/anomaly_scores.parquet"); review=pd.read_csv(out/"predictions_or_scores/review_candidates.csv")
    required={"historical_zscore","iforest_anomaly_score","method_agreement","review_status"}
    assert required<=set(scores.columns) and set(review.review_status)=={"UNREVIEWED"}
    assert not {"accuracy","precision","recall","f1","roc_auc"}&set(result["test_metrics"])
    state=joblib.load(out/"models/isolation_forest.joblib"); assert state["score_orientation"]=="higher_is_more_anomalous"
