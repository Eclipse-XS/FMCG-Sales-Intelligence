from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from fmcg_sales_intelligence.science import run_experiment
from fmcg_sales_intelligence.science.stockout import (DEFAULT_CONFIG, DEFAULT_DATA, DEFAULT_EPISODES,
    assign_episode_ids, baseline_probabilities, classification_metrics, feature_contract,
    fit_model, load_contract, purge_shared_episodes, select_f1_threshold, temporal_split)


def contract_data():
    cfg, data, episodes = load_contract(DEFAULT_CONFIG, DEFAULT_DATA, DEFAULT_EPISODES)
    return cfg, assign_episode_ids(data, episodes), episodes


def test_target_and_episode_mapping_are_stable():
    cfg, data, episodes = contract_data()
    assert cfg["target"] == "stockout_within_7d"
    assert data.stockout_within_7d.sum() == 548
    assert data.loc[data.stockout_within_7d, "analytical_episode_id"].notna().all()
    assert data.loc[data.stockout_within_7d, "analytical_episode_id"].nunique() == len(episodes) == 73
    second = assign_episode_ids(data.drop(columns="analytical_episode_id"), episodes)
    assert second.analytical_episode_id.equals(data.analytical_episode_id)


def test_temporal_boundaries_embargo_and_expected_counts():
    cfg, data, _ = contract_data(); data=data[data.event_observed|data.horizon_complete]
    train, val = temporal_split(data,cfg,"selection_train"),temporal_split(data,cfg,"validation")
    final,test=temporal_split(data,cfg,"final_train"),temporal_split(data,cfg,"test")
    assert (len(train),len(val),len(final),len(test)) == (6720,2688,10752,3840)
    assert train.prediction_date.max()+pd.Timedelta(days=7) < val.prediction_date.min()
    assert final.prediction_date.max()+pd.Timedelta(days=7) < test.prediction_date.min()


def test_episode_purge_removes_only_shared_training_episode():
    rows=pd.DataFrame({"stockout_within_7d":[True,False,True],"analytical_episode_id":["E1",pd.NA,"E2"],"prediction_date":pd.to_datetime(["2024-01-01"]*3)})
    evaluation=pd.DataFrame({"stockout_within_7d":[True],"analytical_episode_id":["E1"]})
    purged,diag=purge_shared_episodes(rows,evaluation)
    assert set(purged.analytical_episode_id.dropna())=={"E2"}
    assert diag["rows_removed"]==1 and diag["shared_episode_ids"]==["E1"]


def test_actual_partition_episode_independence_after_purge():
    cfg,data,_=contract_data(); data=data[data.event_observed|data.horizon_complete]
    for a,b in [("selection_train","validation"),("final_train","test")]:
        train,ev=temporal_split(data,cfg,a),temporal_split(data,cfg,b)
        purged,_=purge_shared_episodes(train,ev)
        assert not (set(purged.loc[purged.stockout_within_7d,"analytical_episode_id"]) & set(ev.loc[ev.stockout_within_7d,"analytical_episode_id"]))


def test_feature_contract_excludes_leakage_and_ids_are_categorical():
    cfg,_,_=contract_data(); numeric,categorical,features=feature_contract(cfg)
    assert not set(features)&set(cfg["forbidden_features"])
    assert {"warehouse_id","sku_id"}.issubset(categorical)
    assert not {"warehouse_id","sku_id"}&set(numeric)


def test_baseline_semantics_and_metrics():
    frame=pd.DataFrame({"available_quantity":[5,20,10],"reorder_point":[10,10,10],"safety_stock":[6,6,6],"sales_velocity_7d":[1,0,2]})
    b=baseline_probabilities(frame)
    assert b["always_no_stockout"].tolist()==[0,0,0]
    assert b["below_reorder_point"].tolist()==[1,0,1]
    assert b["below_safety_stock"].tolist()==[1,0,0]
    assert b["days_of_cover_rule"].tolist()==[1,0,1]
    m=classification_metrics([0,1],[.1,.9],.5)
    assert m["average_precision"]==1 and np.isclose(m["brier"],.01)


def test_threshold_is_derived_from_validation_arrays_and_applied():
    y=np.array([0,0,1,1]); p=np.array([.1,.4,.5,.9])
    threshold,m=select_f1_threshold(y,p)
    assert threshold==.5 and m["f1"]==1


def test_both_models_handle_unseen_categories_and_predict_proba():
    cfg,data,_=contract_data(); data=data[data.event_observed|data.horizon_complete]
    train=temporal_split(data,cfg,"selection_train"); numeric,categorical,features=feature_contract(cfg)
    sample=pd.concat([train[train.stockout_within_7d].head(40),train[~train.stockout_within_7d].head(200)])
    unseen=sample.head(3).copy(); unseen["warehouse_id"]=999; unseen["sku_id"]=999
    for name in cfg["candidate_models"]:
        model=fit_model(name,sample,numeric,categorical,cfg)
        p=model.predict_proba(unseen[features])[:,1]
        assert len(p)==3 and np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
        blob=Path(".pytest_cache")/f"{name}.joblib"; blob.parent.mkdir(exist_ok=True); joblib.dump(model,blob)
        assert np.allclose(joblib.load(blob).predict_proba(unseen[features]),model.predict_proba(unseen[features]))


def test_public_api_dispatch_does_not_break_forecasting_symbol():
    assert callable(run_experiment)
    try: run_experiment("unsupported")
    except ValueError: pass
    else: raise AssertionError("unsupported task must fail")
