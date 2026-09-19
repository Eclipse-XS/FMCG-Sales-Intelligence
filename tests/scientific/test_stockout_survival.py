import numpy as np
import pandas as pd
import yaml
from lifelines import KaplanMeierFitter

from fmcg_sales_intelligence.science import run_experiment
from fmcg_sales_intelligence.science.stockout import DEFAULT_DATA, DEFAULT_EPISODES, load_contract
from fmcg_sales_intelligence.science.survival import (CLASSIFICATION_CONFIG, DEFAULT_CONFIG, build_survival_cohort,
    fit_cox, horizon_metrics, predict_bundle, purge_shared_survival_events,
    survival_c_index, survival_feature_contract)


def cohort():
    _,data,episodes=load_contract(CLASSIFICATION_CONFIG,DEFAULT_DATA,DEFAULT_EPISODES)
    return build_survival_cohort(data,episodes)+(episodes,)


def test_duration_event_and_censoring_contract():
    frame,diag,_=cohort()
    assert (frame.duration_days>0).all()
    assert set(frame.survival_event.unique())<={True,False}
    assert (frame.loc[frame.survival_event,"duration_days"]==frame.loc[frame.survival_event,"event_time_days"]).all()
    assert (frame.loc[~frame.survival_event,"duration_days"]==frame.loc[~frame.survival_event,"censor_time_days"]).all()
    assert (~frame.survival_event).any()  # censored rows remain censored, not events
    assert diag["eligible_at_risk_origins"]==len(frame)


def test_primary_risk_set_excludes_active_stockout_and_zero_followup():
    frame,diag,_=cohort()
    assert (frame.available_quantity>0).all()
    assert diag["active_stockout_origins_excluded"]>0
    assert diag["zero_followup_origins_excluded"]>0


def test_survival_feature_contract_excludes_outcomes_and_ids():
    cfg=yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8")); features=survival_feature_contract(cfg)
    assert not set(features)&set(cfg["forbidden_features"])
    assert "warehouse_id" not in features and "sku_id" not in features


def test_survival_boundary_event_purge():
    train=pd.DataFrame({"survival_event":[True,False],"analytical_episode_id":["E1",pd.NA],"prediction_date":pd.to_datetime(["2024-01-01"]*2)})
    evaluation=pd.DataFrame({"survival_event":[True],"analytical_episode_id":["E1"]})
    purged,diag=purge_shared_survival_events(train,evaluation)
    assert len(purged)==1 and diag["events_removed"]==1


def test_kaplan_meier_and_c_index_orientation():
    km=KaplanMeierFitter().fit([1,2,3],[1,0,1])
    assert 0<=km.predict(2)<=1
    assert survival_c_index([1,2,3],[1,1,1],[3,2,1])==1


def test_cox_fit_predict_and_serializable_contract():
    cfg=yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8")); frame,_,_=cohort(); features=survival_feature_contract(cfg)
    sample=pd.concat([frame[frame.survival_event].head(100),frame[~frame.survival_event].head(300)])
    bundle=fit_cox(sample,features,1.0); pred=predict_bundle(bundle,sample.head(10),[3,5,7])
    assert np.isfinite(pred.to_numpy()).all()
    assert (pred.risk_score>0).all()
    assert ((pred.filter(like="survival_probability")>=0)&(pred.filter(like="survival_probability")<=1)).all().all()


def test_horizon_brier_refuses_early_censoring():
    frame=pd.DataFrame({"duration_days":[2.,5.],"survival_event":[False,True]})
    pred=pd.DataFrame({"survival_probability_day_3":[.8,.7]})
    metrics,mean=horizon_metrics(frame,pred,[3])
    assert metrics["3"]["brier"] is None and mean is None


def test_public_api_survival_dispatch_symbol():
    assert callable(run_experiment)
