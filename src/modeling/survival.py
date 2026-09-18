from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import joblib
import lifelines
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import sklearn
import yaml
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import proportional_hazard_test
from lifelines.utils import concordance_index
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .stockout import (DEFAULT_DATA, DEFAULT_EPISODES, assign_episode_ids,
                       load_contract as load_stockout_contract,
                       temporal_split)

ROOT=Path(__file__).resolve().parents[2]


def _portable_path(path):
    resolved=Path(path).resolve()
    try:return resolved.relative_to(ROOT).as_posix()
    except ValueError:return resolved.as_posix()
DEFAULT_CONFIG=ROOT/"configs/modeling/stockout_survival.yaml"
CLASSIFICATION_CONFIG=ROOT/"configs/modeling/stockout_classification.yaml"


def _write(path,value): path.write_text(json.dumps(value,indent=2,default=str),encoding="utf-8")


def _git():
    def run(*args):
        p=subprocess.run(["git",*args],cwd=ROOT,text=True,capture_output=True)
        return p.stdout.strip() if p.returncode==0 else None
    return {"commit":run("rev-parse","HEAD"),"branch":run("branch","--show-current"),"dirty":bool(run("status","--porcelain"))}


def build_survival_cohort(data: pd.DataFrame, episodes: pd.DataFrame):
    mapped=assign_episode_ids(data,episodes)
    mapped["duration_days"]=np.where(mapped.event_observed,mapped.event_time_days,mapped.censor_time_days)
    mapped["survival_event"]=mapped.event_observed.astype(bool)
    active=mapped.available_quantity<=0
    zero_followup=pd.to_numeric(mapped.duration_days,errors="coerce").fillna(0)<=0
    eligible=mapped.loc[~active&~zero_followup].copy()
    eligible["duration_days"]=eligible.duration_days.astype(float)
    if (eligible.duration_days<=0).any(): raise ValueError("Survival durations must be positive")
    return eligible,{"total_origins":len(mapped),"active_stockout_origins_excluded":int(active.sum()),
                      "zero_followup_origins_excluded":int((~active&zero_followup).sum()),"eligible_at_risk_origins":len(eligible)}


def survival_feature_contract(cfg):
    features=list(cfg["model_features"])
    overlap=set(features)&set(cfg["forbidden_features"])
    if overlap: raise ValueError(f"Survival leakage features: {sorted(overlap)}")
    return features


def purge_shared_survival_events(train,evaluation):
    train_ids=set(train.loc[train.survival_event,"analytical_episode_id"].dropna())
    eval_ids=set(evaluation.loc[evaluation.survival_event,"analytical_episode_id"].dropna())
    shared=train_ids&eval_ids; remove=train.analytical_episode_id.isin(shared)
    return train.loc[~remove].copy(),{"shared_episode_ids":sorted(shared),"rows_removed":int(remove.sum()),
        "events_removed":int((remove&train.survival_event).sum()),"dates_removed":sorted(train.loc[remove,"prediction_date"].dt.strftime("%Y-%m-%d").unique().tolist())}


def survival_c_index(duration,event,risk):
    """Harrell C-index; higher risk is passed with negative orientation."""
    return float(concordance_index(np.asarray(duration,float),-np.asarray(risk,float),np.asarray(event,bool)))


def fit_cox(frame,features,penalizer):
    prep=Pipeline([("imputer",SimpleImputer(strategy="median",add_indicator=False)),("scaler",StandardScaler())])
    x=prep.fit_transform(frame[features]); design=pd.DataFrame(x,columns=features,index=frame.index)
    design["duration_days"]=frame.duration_days.to_numpy(); design["survival_event"]=frame.survival_event.astype(bool).to_numpy()
    model=CoxPHFitter(penalizer=float(penalizer),l1_ratio=0.0)
    model.fit(design,duration_col="duration_days",event_col="survival_event",show_progress=False)
    return {"preprocessor":prep,"model":model,"features":features,"penalizer":float(penalizer)}


def predict_bundle(bundle,frame,horizons=(3,5,7)):
    x=bundle["preprocessor"].transform(frame[bundle["features"]])
    design=pd.DataFrame(x,columns=bundle["features"],index=frame.index)
    risk=bundle["model"].predict_partial_hazard(design).to_numpy()
    surv=bundle["model"].predict_survival_function(design,times=list(horizons)).T
    result={"risk_score":risk}
    for h in horizons: result[f"survival_probability_day_{h}"]=surv[h].to_numpy()
    return pd.DataFrame(result,index=frame.index)


def km_summary(frame,horizons):
    km=KaplanMeierFitter().fit(frame.duration_days,event_observed=frame.survival_event)
    median=None if np.isinf(km.median_survival_time_) else float(km.median_survival_time_)
    return km,{"survival_probability":{str(h):float(km.predict(h)) for h in horizons},"median_survival_days":median}


def horizon_metrics(frame,pred,horizons):
    out={}
    for h in horizons:
        early_censored=(~frame.survival_event)&(frame.duration_days<h)
        if early_censored.any():
            out[str(h)]={"brier":None,"reason":"requires IPCW because censoring precedes horizon","early_censored":int(early_censored.sum())}
            continue
        observed_event_by_h=frame.survival_event&(frame.duration_days<=h)
        event_free=(~observed_event_by_h).astype(float)
        probability=pred[f"survival_probability_day_{h}"].to_numpy()
        out[str(h)]={"brier":float(np.mean((probability-event_free)**2)),"mean_predicted_survival":float(probability.mean()),
                     "observed_event_free_rate":float(event_free.mean()),"early_censored":0}
    valid=[v["brier"] for v in out.values() if v["brier"] is not None]
    return out,float(np.mean(valid)) if valid else None


def ph_diagnostics(bundle,frame):
    x=bundle["preprocessor"].transform(frame[bundle["features"]])
    design=pd.DataFrame(x,columns=bundle["features"],index=frame.index)
    design["duration_days"]=frame.duration_days.to_numpy(); design["survival_event"]=frame.survival_event.astype(bool).to_numpy()
    try:
        result=proportional_hazard_test(bundle["model"],design,time_transform="rank")
        rows=result.summary.reset_index().rename(columns={"index":"feature"}).to_dict("records")
        return {"status":"completed","method":"Schoenfeld residual rank transform","features_p_lt_0_05":[r["feature"] for r in rows if r["p"]<.05],"results":rows}
    except Exception as exc:
        return {"status":"failed_gracefully","reason":f"{type(exc).__name__}: {exc}"}


def _partition(frame,episodes):
    return {"start":str(frame.prediction_date.min().date()),"end":str(frame.prediction_date.max().date()),"rows":len(frame),
            "events":int(frame.survival_event.sum()),"censored":int((~frame.survival_event).sum()),
            "event_fraction":float(frame.survival_event.mean()),"represented_physical_events":int(frame.loc[frame.survival_event,"analytical_episode_id"].nunique()),
            "episode_starts_in_anchor_period":int(episodes.episode_start.between(frame.prediction_date.min(),frame.prediction_date.max()).sum()),
            "median_duration":float(frame.duration_days.median())}


def _sha(path):
    h=hashlib.sha256();
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()


def run_survival_experiment(*,config_path=DEFAULT_CONFIG,data_path=DEFAULT_DATA,episode_path=DEFAULT_EPISODES,
                            output_dir=None,experiment_id=None,overwrite=False):
    cfg=yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    split_cfg,data,episodes=load_stockout_contract(CLASSIFICATION_CONFIG,data_path,episode_path)
    cohort,eligibility=build_survival_cohort(data,episodes); features=survival_feature_contract(cfg); horizons=cfg["evaluation_horizons_days"]
    experiment_id=experiment_id or f"stockout_survival_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_{np.random.default_rng().integers(16**6):06x}"
    out=Path(output_dir) if output_dir else ROOT/"artifacts/experiments/stockout_survival"/experiment_id
    if out.exists():
        if not overwrite:raise FileExistsError(out)
        shutil.rmtree(out)
    for d in [out/"models",out/"predictions",out/"diagnostics",out/"figures"]:d.mkdir(parents=True,exist_ok=True)
    parts={n:temporal_split(cohort,split_cfg,n) for n in ["selection_train","validation","final_train","test"]}
    pre={n:_partition(f,episodes) for n,f in parts.items()}
    if parts["selection_train"].prediction_date.max()+pd.Timedelta(days=cfg["horizon_days"])>=parts["validation"].prediction_date.min():raise ValueError("Selection survival boundary violated")
    if parts["final_train"].prediction_date.max()+pd.Timedelta(days=cfg["horizon_days"])>=parts["test"].prediction_date.min():raise ValueError("Test survival boundary violated")
    parts["selection_train"],p1=purge_shared_survival_events(parts["selection_train"],parts["validation"])
    parts["final_train"],p2=purge_shared_survival_events(parts["final_train"],parts["test"])
    post={n:_partition(f,episodes) for n,f in parts.items()}; split_diag={"pre_control":pre,"post_control":post,"selection_to_validation":p1,"final_train_to_test":p2}
    _write(out/"diagnostics/split_diagnostics.json",split_diag)
    # Descriptive KM is based on selection train and does not select the Cox model.
    km,km_stats=km_summary(parts["selection_train"],horizons)
    ax=km.plot_survival_function();ax.set(xlabel="Days",ylabel="P(stockout-free)",title="Kaplan–Meier: selection train at-risk origins");plt.tight_layout();plt.savefig(out/"figures/kaplan_meier.png",dpi=180);plt.close()
    validation_results={}; bundles={}; val_predictions={}
    for penalizer in cfg["cox_penalizers"]:
        key=f"cox_l2_{penalizer}"; bundle=fit_cox(parts["selection_train"],features,penalizer)
        pred=predict_bundle(bundle,parts["validation"],horizons); c=survival_c_index(parts["validation"].duration_days,parts["validation"].survival_event,pred.risk_score)
        validation_results[key]={"penalizer":float(penalizer),"concordance_index":c,"ph_diagnostics":ph_diagnostics(bundle,parts["selection_train"])}
        bundles[key]=bundle;val_predictions[key]=pred
    selected=max(validation_results,key=lambda k:validation_results[k]["concordance_index"]); selected_bundle=bundles[selected]
    # Validate downstream machinery before freeze/test access.
    val_out=parts["validation"][["prediction_date","warehouse_id","sku_id","duration_days","survival_event","analytical_episode_id"]].join(val_predictions[selected])
    pl.from_pandas(val_out).write_parquet(out/"predictions/validation_predictions.parquet")
    joblib.dump(selected_bundle,out/"models/selection_model.joblib"); reloaded=joblib.load(out/"models/selection_model.joblib")
    if not np.allclose(predict_bundle(reloaded,parts["validation"].head(10),horizons).risk_score,val_predictions[selected].risk_score.head(10)):raise RuntimeError("Validation serialization smoke failed")
    ph=validation_results[selected]["ph_diagnostics"];_write(out/"diagnostics/ph_diagnostics.json",ph)
    coef=selected_bundle["model"].summary.reset_index().rename(columns={"covariate":"feature"})
    coef[[c for c in ["feature","coef","exp(coef)","se(coef)","p","exp(coef) lower 95%","exp(coef) upper 95%"] if c in coef]].to_csv(out/"diagnostics/coefficient_diagnostics.csv",index=False)
    plt.figure(figsize=(7,4));order=np.argsort(coef["coef"]);plt.barh(coef.iloc[order]["feature"],coef.iloc[order]["coef"]);plt.axvline(0,color="black",lw=.8);plt.xlabel("Cox coefficient");plt.tight_layout();plt.savefig(out/"figures/cox_coefficients.png",dpi=180);plt.close()
    frozen={"selected_model":"cox_proportional_hazards","selected_configuration":selected,"penalizer":validation_results[selected]["penalizer"],
            "features":features,"preprocessing":"train-fitted median imputation and standard scaling","duration_definition":cfg["duration_definition"],
            "event_definition":cfg["event_definition"],"cohort_eligibility":cfg["risk_set"],"boundary_policy":f"{cfg['horizon_days']}-day embargo plus physical-event purge",
            "validation_concordance_index":validation_results[selected]["concordance_index"],"random_seed":cfg["random_seed"],
            "split_fingerprint":hashlib.sha256(json.dumps(split_cfg["split"],sort_keys=True,default=str).encode()).hexdigest(),
            "physical_event_control_fingerprint":hashlib.sha256(json.dumps(split_diag,sort_keys=True,default=str).encode()).hexdigest(),
            "library":f"lifelines {lifelines.__version__}","test_accessed":False}
    _write(out/"selected_model.json",frozen)
    # Test is first accessed only after all validation machinery and frozen selection exist.
    final=fit_cox(parts["final_train"],features,frozen["penalizer"]); test_pred=predict_bundle(final,parts["test"],horizons)
    test_c=survival_c_index(parts["test"].duration_days,parts["test"].survival_event,test_pred.risk_score)
    horizon,test_ibs=horizon_metrics(parts["test"],test_pred,horizons)
    test_out=parts["test"][["prediction_date","warehouse_id","sku_id","duration_days","survival_event","analytical_episode_id","available_quantity","sales_velocity_7d"]].join(test_pred)
    test_out["partition"]="test";test_out["is_out_of_sample"]=True;pl.from_pandas(test_out).write_parquet(out/"predictions/test_predictions.parquet")
    joblib.dump(final,out/"models/final_model.joblib");loaded=joblib.load(out/"models/final_model.joblib")
    if not np.allclose(predict_bundle(loaded,parts["test"].head(10),horizons),test_pred.head(10)):raise RuntimeError("Final model reload smoke failed")
    final_ph=ph_diagnostics(final,parts["final_train"]);_write(out/"diagnostics/final_ph_diagnostics.json",final_ph)
    final_coef=final["model"].summary.reset_index().rename(columns={"covariate":"feature"});final_coef.to_csv(out/"diagnostics/final_coefficients.csv",index=False)
    censor_diag={"eligibility":eligibility,"overall":{"events":int(cohort.survival_event.sum()),"censored":int((~cohort.survival_event).sum()),"censoring_fraction":float((~cohort.survival_event).mean())},
                 "censor_durations":cohort.loc[~cohort.survival_event,"duration_days"].value_counts().sort_index().to_dict(),
                 "dataset_end_censored":int(((~cohort.survival_event)&(cohort.duration_days<cfg["horizon_days"])).sum()),"administrative_7d_censored":int(((~cohort.survival_event)&(cohort.duration_days==cfg["horizon_days"])).sum())}
    _write(out/"diagnostics/censoring_diagnostics.json",censor_diag)
    corr=cohort[cfg["features"]].astype(float).corr();upper=corr.where(np.triu(np.ones(corr.shape),1).astype(bool)).stack().abs().sort_values(ascending=False)
    multicol={"predeclared_reduced_features":features,"excluded_correlated_or_derived_features":sorted(set(cfg["features"])-set(features)),"largest_absolute_correlations":{f"{a}|{b}":float(v) for (a,b),v in upper.head(10).items()},"fitted_coefficients":len(features),"physical_events":len(episodes),"events_per_parameter":len(episodes)/len(features)}
    _write(out/"diagnostics/multicollinearity.json",multicol)
    shift={n:{"event_fraction":float(f.survival_event.mean()),"median_duration":float(f.duration_days.median()),"mean_available":float(f.available_quantity.mean()),"mean_velocity":float(f.sales_velocity_7d.mean()),"mean_replenishment":float(f.replenishment_sum_7d.astype(float).mean())} for n,f in parts.items()}
    _write(out/"diagnostics/temporal_shift.json",shift)
    event_risk=test_out[test_out.survival_event].groupby("duration_days").risk_score.agg(["count","mean","median"]).reset_index();event_risk.to_csv(out/"diagnostics/risk_by_days_to_event.csv",index=False)
    plt.figure(figsize=(6,4));plt.plot(event_risk.duration_days,event_risk["mean"],"o-");plt.xlabel("Observed days to event");plt.ylabel("Mean partial hazard");plt.tight_layout();plt.savefig(out/"figures/risk_by_days_to_event.png",dpi=180);plt.close()
    examples=[(test_pred.risk_score-v).abs().idxmin() for v in test_pred.risk_score.quantile([.1,.5,.9]).to_numpy()]
    curves=final["model"].predict_survival_function(pd.DataFrame(final["preprocessor"].transform(parts["test"].loc[examples,features]),columns=features,index=examples),times=horizons)
    curves.plot(figsize=(6,4));plt.xlabel("Days");plt.ylabel("Predicted survival");plt.tight_layout();plt.savefig(out/"figures/representative_survival_curves.png",dpi=180);plt.close()
    metrics={"kaplan_meier_selection_train":km_stats,"validation_candidates":validation_results,"selection":{"configuration":selected,"penalizer":frozen["penalizer"],"concordance_index":frozen["validation_concordance_index"]},
             "test":{"concordance_index":test_c,"horizon_metrics":horizon,"mean_supported_horizon_brier":test_ibs,"rows":len(parts["test"]),"events":int(parts["test"].survival_event.sum()),"censored":int((~parts["test"].survival_event).sum()),"represented_physical_events":post["test"]["represented_physical_events"]}}
    _write(out/"metrics.json",metrics);_write(out/"dvc_metrics.json",{"test_concordance_index":test_c,"test_mean_supported_horizon_brier":test_ibs,"test_events":metrics["test"]["events"],"test_censored":metrics["test"]["censored"],"physical_episodes":len(episodes)})
    shutil.copy2(config_path,out/"resolved_config.yaml")
    manifest={"experiment_id":experiment_id,"task":"stockout_survival","status":"completed","created_at_utc":datetime.now(timezone.utc).isoformat(),"dataset_path":_portable_path(data_path),"dataset_sha256":_sha(data_path),
              "schema":{c:str(t) for c,t in pl.read_parquet_schema(data_path).items()},"duration_definition":cfg["duration_definition"],"event_definition":cfg["event_definition"],"censoring_definition":cfg["censoring_definition"],"risk_set":cfg["risk_set"],"prediction_moment":cfg["time_origin"],
              "features":features,"forbidden_features":cfg["forbidden_features"],"partitions":split_diag,"selected_model":frozen,"test_metrics":metrics["test"],"ph_summary":final_ph,"coefficient_stability":multicol,
              "random_seed":cfg["random_seed"],"versions":{"python":platform.python_version(),"lifelines":lifelines.__version__,"sklearn":sklearn.__version__},"git":_git(),"model_reload_smoke":"passed"}
    _write(out/"manifest.json",manifest)
    violations=final_ph.get("features_p_lt_0_05",[])
    report=f"""# Stockout Survival V1

## Objective and contract
Estimate time from an at-risk inventory snapshot `t` to first future physical stockout onset within seven days. This differs from Classification V1: censored origins remain censored and are not negatives. Duration is `{cfg['duration_definition']}` and event is `{cfg['event_definition']}`.

## Cohort, censoring and dependence
From {eligibility['total_origins']:,} origins, {eligibility['active_stockout_origins_excluded']} active-stockout and {eligibility['zero_followup_origins_excluded']} zero-follow-up origins are excluded, leaving {eligibility['eligible_at_risk_origins']:,}. There are {int(cohort.survival_event.sum())} event rows but only {len(episodes)} physical episodes; repeated daily origins and entities violate iid interpretation. No-event rows are administratively censored at day 7 or earlier at dataset end.

## Temporal boundary control and leakage
Configured chronological blocks use a {cfg['horizon_days']}-day embargo; physical-event purge removed {p1['rows_removed']} and {p2['rows_removed']} training rows. Inputs are the predeclared reduced point-in-time set `{', '.join(features)}`. Outcome, censoring, episode and future fields are excluded. Historical replenishment covers `[t-7,t)` only.

## Kaplan–Meier
Selection-train stockout-free probabilities are {km_stats['survival_probability']}. Median survival is {'not reached' if km_stats['median_survival_days'] is None else km_stats['median_survival_days']} within the modeled horizon.

## Cox selection, assumptions and final evaluation
Predeclared L2 penalizers {cfg['cox_penalizers']} were compared on validation C-index. `{selected}` was frozen at penalizer {frozen['penalizer']} with validation C-index {frozen['validation_concordance_index']:.4f}. Final test C-index is {test_c:.4f} on {len(parts['test'])} origins, {metrics['test']['events']} observed-event rows and {post['test']['represented_physical_events']} represented physical events. Mean supported horizon Brier is {test_ibs:.4f}. Schoenfeld diagnostics flag {violations or 'no feature at p<0.05'}, but p-values are descriptive because repeated origins invalidate classical independence.

## Coefficients, stability and interpretation
The model has {len(features)} coefficients for {len(episodes)} physical episodes ({len(episodes)/len(features):.1f} events per parameter as a descriptive ratio). Hazard ratios describe conditional association, not causation. Correlated inventory identities were excluded before fitting; L2 regularization remains necessary.

## Limitations and future hypotheses
This is a synthetic ~90-day, seven-day landmark experiment, not a recurrent-event model. Absolute survival calibration is limited, administrative censoring dominates, origins are dependent, and event support is small. Future work may use a longer event table, explicit pending-order state, and a formally clustered/recurrent-event design; none is implemented here.
"""
    (out/"report.md").write_text(report,encoding="utf-8")
    return {"experiment_id":experiment_id,"output_dir":str(out),"selected_model":"cox_proportional_hazards","selected_configuration":selected,"test_metrics":metrics["test"]}
