"""Sales Anomaly Detection V1: post-event, unsupervised candidate scoring."""
from __future__ import annotations

import hashlib, json, platform, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import yaml
from scipy.stats import spearmanr
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_CONFIG=ROOT/"configs/modeling/anomaly.yaml"
DEFAULT_DATA=ROOT/"data/processed/anomaly/anomaly_v1.parquet"

def _sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def _git(*args):
    try:return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
    except Exception:return None

def load_data(config_path=DEFAULT_CONFIG,data_path=DEFAULT_DATA):
    cfg=yaml.safe_load(Path(config_path).read_text(encoding="utf-8")); d=pd.read_parquet(data_path)
    d["event_date"]=pd.to_datetime(d.event_date)
    for c in ["event_observed_units","event_transaction_unit_price","lag_1","lag_7","rolling_mean_7d","rolling_std_7d"]: d[c]=pd.to_numeric(d[c],errors="coerce")
    return cfg,d.sort_values(["store_id","sku_id","event_date"]).reset_index(drop=True)

def recompute_historical_stats(frame,window_days=7):
    """Strict `[t-window,t)` positive-event statistics by store/SKU."""
    out=frame.copy(); means=np.full(len(out),np.nan); stds=np.full(len(out),np.nan); counts=np.zeros(len(out),dtype=int)
    for _,idx in out.groupby(["store_id","sku_id"],sort=False).groups.items():
        pos=np.asarray(list(idx)); dates=out.loc[pos,"event_date"].to_numpy(dtype="datetime64[ns]"); vals=out.loc[pos,"event_observed_units"].to_numpy(float)
        for j,p in enumerate(pos):
            mask=(dates<dates[j])&(dates>=dates[j]-np.timedelta64(window_days,"D")); hist=vals[mask]; counts[p]=len(hist)
            if len(hist): means[p]=hist.mean()
            if len(hist)>=2: stds[p]=hist.std(ddof=1)
    out["historical_count_7d"]=counts; out["historical_mean_7d"]=means; out["historical_std_7d"]=stds
    return out

def score_z_baseline(frame,cfg):
    out=recompute_historical_stats(frame,cfg["rolling"]["window_days"]); minimum=cfg["rolling"]["minimum_positive_event_history"]
    scorable=out.historical_count_7d.ge(minimum)&out.historical_std_7d.notna(); delta=out.event_observed_units-out.historical_mean_7d
    z=pd.Series(np.nan,index=out.index,dtype=float); regular=scorable&out.historical_std_7d.gt(0); z.loc[regular]=delta.loc[regular]/out.loc[regular,"historical_std_7d"]
    constant=scorable&out.historical_std_7d.eq(0); z.loc[constant&delta.eq(0)]=0.; z.loc[constant&delta.gt(0)]=np.inf; z.loc[constant&delta.lt(0)]=-np.inf
    out["zscore_scorable"]=scorable; out["zscore_status"]=np.where(scorable,"SCORABLE","NOT_SCORABLE_INSUFFICIENT_HISTORY"); out["historical_zscore"]=z; out["abs_historical_zscore"]=z.abs(); out["zscore_direction"]=np.select([z.ge(cfg["rolling"]["threshold_abs_z"]),z.le(-cfg["rolling"]["threshold_abs_z"])],["HIGH","LOW"],default="NONE"); out["zscore_candidate"]=scorable&z.abs().ge(cfg["rolling"]["threshold_abs_z"])
    return out

def temporal_masks(frame,cfg):
    ref=cfg["temporal_design"]["reference"]; scoring=cfg["temporal_design"]["scoring"]
    return frame.event_date.between(pd.Timestamp(ref["start"]),pd.Timestamp(ref["end"])),frame.event_date.between(pd.Timestamp(scoring["start"]),pd.Timestamp(scoring["end"]))

def fit_iforest(reference,cfg,seed=None,contamination=None):
    features=cfg["features"]; pre=Pipeline([("imputer",SimpleImputer(strategy="median",add_indicator=True)),("scaler",StandardScaler())]); X=pre.fit_transform(reference[features])
    spec=cfg["isolation_forest"]; model=IsolationForest(n_estimators=spec["n_estimators"],contamination=contamination or spec["contamination"],random_state=seed or cfg["random_seed"],n_jobs=-1).fit(X)
    return pre,model

def canonical_iforest_score(pre,model,frame,features):
    return -model.decision_function(pre.transform(frame[features]))

def agreement(scoring):
    z=scoring.zscore_candidate.to_numpy(bool); i=scoring.iforest_candidate.to_numpy(bool); both=int((z&i).sum()); zo=int((z&~i).sum()); io=int((~z&i).sum()); neither=int((~z&~i).sum()); union=both+zo+io
    return {"both_flagged_count":both,"zscore_only_count":zo,"iforest_only_count":io,"neither_count":neither,"intersection_count":both,"union_count":union,"jaccard_agreement":both/union if union else None,"overlap_fraction_of_zscore":both/int(z.sum()) if z.sum() else None,"overlap_fraction_of_iforest":both/int(i.sum()) if i.sum() else None}

def detect_runs(frame,flag_col,method):
    x=frame[frame[flag_col].astype(bool)].sort_values(["store_id","sku_id","event_date"]).copy()
    if x.empty:return pd.DataFrame(columns=["method","store_id","sku_id","run_start","run_end","run_length"])
    x["new_run"]=x.groupby(["store_id","sku_id"]).event_date.diff().dt.days.ne(1); x["run_id"]=x.groupby(["store_id","sku_id"]).new_run.cumsum()
    r=x.groupby(["store_id","sku_id","run_id"]).event_date.agg(run_start="min",run_end="max",run_length="size").reset_index(); r.insert(0,"method",method); return r.drop(columns="run_id")

def run_anomaly_experiment(config_path=DEFAULT_CONFIG,data_path=DEFAULT_DATA,output_dir=None,experiment_id=None,overwrite=False):
    cfg,d=load_data(config_path,data_path); data_path=Path(data_path)
    if d[["event_date","store_id","sku_id"]].duplicated().any():raise ValueError("Duplicate anomaly event grain")
    forbidden=set(cfg["forbidden_features"])
    if forbidden.intersection(d.columns):
        raise ValueError("Ground-truth/future-derived anomaly field found")
    scored=score_z_baseline(d,cfg)
    # Verify persisted rolling fields against an independent strict-prior recomputation.
    for old,new in [("rolling_mean_7d","historical_mean_7d"),("rolling_std_7d","historical_std_7d")]:
        a=scored[old].to_numpy(float); b=scored[new].to_numpy(float)
        if not np.allclose(a,b,equal_nan=True,atol=1e-10):raise ValueError(f"DATA_ISSUE_FOUND: {old} is not strict-prior [t-7,t)")
    ref_mask,score_mask=temporal_masks(scored,cfg); reference=scored[ref_mask]; evaluation=scored[score_mask].copy()
    if reference.event_date.max()>=evaluation.event_date.min():raise ValueError("Reference/scoring periods overlap")
    pre,model=fit_iforest(reference,cfg); scored["iforest_anomaly_score"]=canonical_iforest_score(pre,model,scored,cfg["features"]); scored["iforest_candidate"]=score_mask&(scored.iforest_anomaly_score>0)
    scored["period"]=np.where(ref_mask,"REFERENCE",np.where(score_mask,"SCORING","OUTSIDE")); scored["method_agreement"]=np.select([scored.zscore_candidate&scored.iforest_candidate,scored.zscore_candidate&~scored.iforest_candidate,~scored.zscore_candidate&scored.iforest_candidate],["BOTH","ZSCORE_ONLY","IFOREST_ONLY"],default="NEITHER"); scored["review_status"]="UNREVIEWED"; scored["inventory_censoring_context"]="UNAVAILABLE_IN_EVENT_ARTIFACT"
    evaluation=scored[score_mask].copy(); agree=agreement(evaluation)
    runs=pd.concat([detect_runs(evaluation,"zscore_candidate","ZSCORE"),detect_runs(evaluation,"iforest_candidate","ISOLATION_FOREST")],ignore_index=True)
    run_summary={m:{"flagged_rows":int(evaluation[col].sum()),"distinct_runs":int((runs.method==m).sum()),"median_run_length":float(runs.loc[runs.method==m,"run_length"].median()) if (runs.method==m).any() else 0,"maximum_run_length":int(runs.loc[runs.method==m,"run_length"].max()) if (runs.method==m).any() else 0} for m,col in [("ZSCORE","zscore_candidate"),("ISOLATION_FOREST","iforest_candidate")]}
    # Predeclared sensitivity; no result selects the canonical contamination.
    sensitivity=[]; canonical_rank=evaluation.iforest_anomaly_score.rank(pct=True)
    top_n=max(1,int(np.ceil(len(evaluation)*.01))); canonical_top=set(evaluation.nlargest(top_n,"iforest_anomaly_score").index)
    for contamination in cfg["isolation_forest"]["sensitivity_contamination"]:
        for seed in cfg["isolation_forest"]["sensitivity_seeds"]:
            p,m=fit_iforest(reference,cfg,seed,contamination); s=pd.Series(canonical_iforest_score(p,m,evaluation,cfg["features"]),index=evaluation.index); flags=s.gt(0); top=set(s.nlargest(top_n).index)
            sensitivity.append({"contamination":contamination,"seed":seed,"candidate_count":int(flags.sum()),"candidate_rate":float(flags.mean()),"top_1pct_jaccard_vs_canonical":len(top&canonical_top)/len(top|canonical_top),"rank_spearman_vs_canonical":float(spearmanr(s,canonical_rank).statistic)})
    sensitivity_df=pd.DataFrame(sensitivity)
    # Serialization and exact reload smoke test.
    state={"preprocessor":pre,"model":model,"features":cfg["features"],"score_orientation":"higher_is_more_anomalous","threshold":0.0,"config":cfg["isolation_forest"]}
    out=Path(output_dir or ROOT/"artifacts/experiments/anomaly"/(experiment_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")))
    if out.exists() and overwrite:shutil.rmtree(out)
    if out.exists():raise FileExistsError(out)
    for p in [out/"models",out/"predictions_or_scores",out/"diagnostics",out/"figures"]:p.mkdir(parents=True,exist_ok=True)
    joblib.dump(state,out/"models/isolation_forest.joblib"); loaded=joblib.load(out/"models/isolation_forest.joblib"); sample=evaluation.head(50); assert np.allclose(canonical_iforest_score(pre,model,sample,cfg["features"]),canonical_iforest_score(loaded["preprocessor"],loaded["model"],sample,loaded["features"]))
    keep=["event_date","store_id","sku_id","event_observed_units","event_transaction_unit_price","event_is_promo","brand_name","category_name","historical_count_7d","historical_mean_7d","historical_std_7d","zscore_scorable","zscore_status","historical_zscore","abs_historical_zscore","zscore_direction","zscore_candidate","iforest_anomaly_score","iforest_candidate","method_agreement","period","inventory_censoring_context","review_status"]
    scored[keep].to_parquet(out/"predictions_or_scores/anomaly_scores.parquet",index=False)
    ranked=evaluation.assign(combined_rank=evaluation.abs_historical_zscore.rank(pct=True).fillna(0)+evaluation.iforest_anomaly_score.rank(pct=True)).sort_values(["method_agreement","combined_rank"],ascending=[True,False]); review=ranked[(ranked.zscore_candidate)|(ranked.iforest_candidate)].head(cfg["review_top_n"]); review[keep].to_csv(out/"predictions_or_scores/review_candidates.csv",index=False)
    runs.to_csv(out/"diagnostics/anomaly_runs.csv",index=False); sensitivity_df.to_csv(out/"diagnostics/sensitivity_metrics.csv",index=False)
    slices=[]
    for field in ["event_is_promo","category_name"]:
        for value,g in evaluation.groupby(field):slices.append({"slice":field,"value":str(value),"rows":len(g),"zscore_rate":g.zscore_candidate.mean(),"iforest_rate":g.iforest_candidate.mean(),"both_count":int(((g.zscore_candidate)&(g.iforest_candidate)).sum())})
    pd.DataFrame(slices).to_csv(out/"diagnostics/slice_metrics.csv",index=False)
    shift={"reference":{"rows":len(reference),"mean_units":reference.event_observed_units.mean(),"promo_rate":reference.event_is_promo.mean(),"mean_price":reference.event_transaction_unit_price.mean()},"scoring":{"rows":len(evaluation),"mean_units":evaluation.event_observed_units.mean(),"promo_rate":evaluation.event_is_promo.mean(),"mean_price":evaluation.event_transaction_unit_price.mean()},"label":"temporal_distribution_shift_not_production_drift"}
    (out/"diagnostics/temporal_shift.json").write_text(json.dumps(shift,indent=2),encoding="utf-8"); (out/"diagnostics/agreement_metrics.json").write_text(json.dumps(agree,indent=2),encoding="utf-8")
    diag={"grain":["event_date","store_id","sku_id"],"rows":len(d),"date_range":[str(d.event_date.min().date()),str(d.event_date.max().date())],"stores":d.store_id.nunique(),"skus":d.sku_id.nunique(),"positive_sales_rows":int((d.event_observed_units>0).sum()),"zero_sales_rows":int((d.event_observed_units==0).sum()),"duplicate_keys":0,"missingness":d.isna().sum().to_dict(),"ground_truth_labels":[],"source_semantics":"positive realized sales events only; absent zero-sales days are not rows","strict_prior_recomputation_match":True}
    (out/"diagnostics/data_diagnostics.json").write_text(json.dumps(diag,indent=2),encoding="utf-8")
    # Figures.
    plt.figure(figsize=(7,5)); plt.scatter(evaluation.abs_historical_zscore.clip(upper=12),evaluation.iforest_anomaly_score,s=7,alpha=.35,c=evaluation.method_agreement.map({"BOTH":"red","ZSCORE_ONLY":"orange","IFOREST_ONLY":"blue","NEITHER":"gray"})); plt.xlabel("Absolute historical z-score (clipped at 12)");plt.ylabel("IF anomaly score (higher = more anomalous)");plt.tight_layout();plt.savefig(out/"figures/score_comparison.png",dpi=180);plt.close()
    daily=evaluation.groupby("event_date")[["zscore_candidate","iforest_candidate"]].mean();daily.plot(figsize=(9,4));plt.ylabel("Candidate rate");plt.tight_layout();plt.savefig(out/"figures/anomaly_rate_over_time.png",dpi=180);plt.close()
    plt.figure(figsize=(8,4));plt.hist(evaluation.iforest_anomaly_score,bins=50);plt.axvline(0,color="red",ls="--",label="flag threshold");plt.xlabel("IF anomaly score");plt.legend();plt.tight_layout();plt.savefig(out/"figures/score_distribution.png",dpi=180);plt.close()
    representative=evaluation.assign(any_flag=evaluation.zscore_candidate|evaluation.iforest_candidate).groupby(["store_id","sku_id"]).any_flag.sum().sort_values(ascending=False).index[0]; series=scored[(scored.store_id==representative[0])&(scored.sku_id==representative[1])]; plt.figure(figsize=(9,4));plt.plot(series.event_date,series.event_observed_units,marker="."); flags=series[series.zscore_candidate|series.iforest_candidate];plt.scatter(flags.event_date,flags.event_observed_units,color="red",label="candidate");plt.title(f"Deterministic highest-candidate series: store {representative[0]}, SKU {representative[1]}");plt.legend();plt.tight_layout();plt.savefig(out/"figures/representative_series.png",dpi=180);plt.close()
    zc=int(evaluation.zscore_candidate.sum());ic=int(evaluation.iforest_candidate.sum()); scorable=int(evaluation.zscore_scorable.sum())
    high=int((evaluation.zscore_candidate&evaluation.zscore_direction.eq("HIGH")).sum()); low=int((evaluation.zscore_candidate&evaluation.zscore_direction.eq("LOW")).sum()); infinite=int(np.isinf(evaluation.historical_zscore).sum())
    metrics={"total_rows":len(d),"reference_rows":len(reference),"scoring_rows":len(evaluation),"scorable_rows":scorable,"insufficient_history_rows":int(len(evaluation)-scorable),"zscore_candidate_count":zc,"zscore_candidate_rate":zc/scorable if scorable else None,"zscore_high_count":high,"zscore_low_count":low,"zscore_zero_variance_candidate_count":infinite,"isolation_forest_candidate_count":ic,"isolation_forest_candidate_rate":ic/len(evaluation),**agree,"zscore_anomaly_run_count":run_summary["ZSCORE"]["distinct_runs"],"iforest_anomaly_run_count":run_summary["ISOLATION_FOREST"]["distinct_runs"],"mean_sensitivity_top_1pct_jaccard":sensitivity_df.top_1pct_jaccard_vs_canonical.mean(),"readiness":"READY_WITH_LIMITATIONS"}
    for name in ["metrics.json","dvc_metrics.json"]:(out/name).write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    selected={"method":"isolation_forest","role":"primary_unsupervised_candidate_not_supervised_winner","feature_set":cfg["features"],"preprocessing":"reference-fitted median imputation with missing indicators and standard scaling","reference_period":cfg["temporal_design"]["reference"],"scoring_period":cfg["temporal_design"]["scoring"],"contamination":cfg["isolation_forest"]["contamination"],"threshold_policy":cfg["isolation_forest"]["threshold_policy"],"decision_threshold":0.0,"score_orientation":"higher_is_more_anomalous","random_seed":cfg["random_seed"],"dataset_fingerprint":_sha(data_path)}; (out/"selected_model.json").write_text(json.dumps(selected,indent=2,default=str),encoding="utf-8"); (out/"resolved_config.yaml").write_text(yaml.safe_dump(cfg,sort_keys=False),encoding="utf-8")
    report=f"""# Sales Anomaly Detection V1

## 1. Objective
Rank unusual positive sales observations for investigation.
## 2. Why this is unsupervised
No independently verified anomaly label exists. Candidate flags are not fraud, errors, or confirmed incidents.
## 3. Dataset and grain
{len(d):,} rows at positive-sales event date × store × SKU grain, {d.store_id.nunique()} stores, {d.sku_id.nunique()} SKUs, {d.event_date.min().date()}—{d.event_date.max().date()}. Zero-sale days are absent.
## 4. Scoring semantics
Post-event scoring uses current observed units/price/promotion plus strict-prior history.
## 5. Feature contract
Isolation Forest features: `{', '.join(cfg['features'])}`. IDs are identity only; brand/category are context only; future fields are forbidden.
## 6. Temporal/reference design
Reference {cfg['temporal_design']['reference']['start']}—{cfg['temporal_design']['reference']['end']} ({len(reference):,} rows); scoring {cfg['temporal_design']['scoring']['start']}—{cfg['temporal_design']['scoring']['end']} ({len(evaluation):,} rows).
## 7. Rolling z-score baseline
`(current units - mean prior positive events in [t-7,t)) / sample std`; minimum {cfg['rolling']['minimum_positive_event_history']} events; threshold |z|≥{cfg['rolling']['threshold_abs_z']}. Current and future rows are excluded.
## 8. Isolation Forest
{cfg['isolation_forest']['n_estimators']} trees, contamination {cfg['isolation_forest']['contamination']}, fitted only on reference. Canonical score is negative decision function, so higher means more unusual.
## 9. Candidate rates
Z-score {zc:,}/{scorable:,} scorable ({zc/scorable:.2%}); Isolation Forest {ic:,}/{len(evaluation):,} ({ic/len(evaluation):.2%}).
## 10. Method agreement
Both {agree['both_flagged_count']:,}; z-score only {agree['zscore_only_count']:,}; IF only {agree['iforest_only_count']:,}; neither {agree['neither_count']:,}; Jaccard {agree['jaccard_agreement']:.3f}.
## 11. Score distributions
Continuous scores are retained. Binary flags are secondary threshold policies.
## 12. High vs low anomalies
Signed z-score and direction are preserved: {high:,} HIGH and {low:,} LOW candidates. {infinite:,} candidates arise from the explicit zero-variance policy, contributing to the high z-score rate; IF is directionless relative unusualness.
## 13. Context analysis
Promotion and category slices are descriptive. Inventory censoring is unavailable in this positive-event artifact.
## 14. Temporal anomaly runs
Z-score: {run_summary['ZSCORE']}. Isolation Forest: {run_summary['ISOLATION_FOREST']}.
## 15. Sensitivity/stability
Predeclared contaminations and three seeds were evaluated without choosing a new canonical threshold. Mean top-1% Jaccard vs canonical: {sensitivity_df.top_1pct_jaccard_vs_canonical.mean():.3f}.
## 16. Representative candidates
The plotted series is selected deterministically by the highest combined candidate count, not visual appeal.
## 17. Forecast residual compatibility
`FORECAST_RESIDUAL_DIAGNOSTIC_NOT_COMPATIBLE`: Forecasting V1 predicts `(t,t+7]` aggregate demand, not same-day positive-event units. It was not retrained or rerun.
## 18. Human-review artifact
Top {len(review)} candidates are `UNREVIEWED`; none is verified.
## 19. Readiness
`READY_WITH_LIMITATIONS` for offline candidate ranking, not production deployment.
## 20. Limitations
Synthetic data, about 90 days, positive-event-only history, no labels, threshold dependence, limited seasonality, contextual confounding, and no production validation.
## 21. Reproducibility/DVC
Fixed seed {cfg['random_seed']}; serialized pipeline/model; dataset/config/code tracked by `anomaly_v1`.
## 22. Future hypotheses
Human review and a daily complete-grid one-step expected-sales model are required before residual-based detection or production claims.
""";(out/"report.md").write_text(report,encoding="utf-8")
    manifest={"experiment_id":experiment_id or out.name,"task":"anomaly_detection","status":"complete","created_at":datetime.now(timezone.utc).isoformat(),"dataset_path":str(data_path),"dataset_fingerprint":_sha(data_path),"schema_fingerprint":hashlib.sha256(str([(c,str(t)) for c,t in zip(d.columns,d.dtypes)]).encode()).hexdigest(),"grain":["event_date","store_id","sku_id"],"date_range":diag["date_range"],"reference_period":cfg["temporal_design"]["reference"],"scoring_period":cfg["temporal_design"]["scoring"],"baseline_definition":cfg["rolling"],"isolation_forest":selected,"feature_observability_policy":"post-event current observation plus strict-prior history","forbidden_future_fields":cfg["forbidden_features"],"context_only_fields":cfg["context_only"],"candidate_counts":{"zscore":zc,"isolation_forest":ic},"agreement_diagnostics":agree,"run_diagnostics":run_summary,"sensitivity_summary":{"rows":len(sensitivity_df),"mean_top_1pct_jaccard":sensitivity_df.top_1pct_jaccard_vs_canonical.mean()},"forecast_residual_compatibility":"FORECAST_RESIDUAL_DIAGNOSTIC_NOT_COMPATIBLE","readiness":"READY_WITH_LIMITATIONS","git":{"commit":_git("rev-parse","HEAD"),"branch":_git("branch","--show-current"),"dirty":bool(_git("status","--porcelain"))},"dvc":{"stage":"anomaly_v1","remote":None},"library_versions":{"python":platform.python_version(),"pandas":pd.__version__,"scikit_learn":sklearn.__version__},"reload_smoke_test":True,"artifacts":{"scores":"predictions_or_scores/anomaly_scores.parquet","review":"predictions_or_scores/review_candidates.csv","model":"models/isolation_forest.joblib"}};(out/"manifest.json").write_text(json.dumps(manifest,indent=2,default=str),encoding="utf-8")
    return {"experiment_id":manifest["experiment_id"],"output_dir":str(out),"selected_model":"isolation_forest","test_metrics":metrics}
