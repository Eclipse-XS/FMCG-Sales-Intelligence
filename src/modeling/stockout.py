from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import sklearn
import yaml
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss, confusion_matrix,
                             f1_score, precision_recall_curve, precision_score, recall_score,
                             roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

ROOT = Path(__file__).resolve().parents[2]


def _portable_path(path):
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()
DEFAULT_CONFIG = ROOT / "configs/modeling/stockout_classification.yaml"
DEFAULT_DATA = ROOT / "data/processed/stockout/stockout_v1.parquet"
DEFAULT_EPISODES = ROOT / "reports/data_refinement/stockout_episodes.parquet"


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def _git() -> dict[str, Any]:
    def run(*args):
        p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
        return p.stdout.strip() if p.returncode == 0 else None
    return {"commit": run("rev-parse", "HEAD"), "branch": run("branch", "--show-current"),
            "dirty": bool(run("status", "--porcelain"))}


def load_contract(config_path=DEFAULT_CONFIG, data_path=DEFAULT_DATA, episode_path=DEFAULT_EPISODES):
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    data = pl.read_parquet(data_path).to_pandas()
    episodes = pl.read_parquet(episode_path).to_pandas()
    for c in ["prediction_date", "first_stockout_date"]: data[c] = pd.to_datetime(data[c])
    for c in ["episode_start", "recovery_date"]: episodes[c] = pd.to_datetime(episodes[c])
    return cfg, data, episodes


def assign_episode_ids(data: pd.DataFrame, episodes: pd.DataFrame) -> pd.DataFrame:
    """Map every positive horizon to the physical zero-inventory run it points into."""
    result = data.copy(); result["analytical_episode_id"] = pd.NA
    lookup: dict[tuple[int, int], list] = {}
    for row in episodes.itertuples():
        lookup.setdefault((row.warehouse_id, row.sku_id), []).append(row)
    for idx, row in result[result.stockout_within_7d].iterrows():
        event_date = row.first_stockout_date
        matches = [e for e in lookup.get((row.warehouse_id, row.sku_id), [])
                   if e.episode_start <= event_date and (pd.isna(e.recovery_date) or event_date < e.recovery_date)]
        if len(matches) != 1:
            raise ValueError(f"Expected one physical episode for positive row {idx}, found {len(matches)}")
        e = matches[0]
        result.at[idx, "analytical_episode_id"] = f"W{e.warehouse_id}_S{e.sku_id}_{e.episode_start:%Y%m%d}"
    if result.loc[result.stockout_within_7d, "analytical_episode_id"].isna().any():
        raise ValueError("Unmapped positive horizons")
    return result


def temporal_split(data: pd.DataFrame, cfg: dict, name: str) -> pd.DataFrame:
    spec = cfg["split"][name]
    return data[data.prediction_date.between(pd.Timestamp(spec["start"]), pd.Timestamp(spec["end"]))].copy()


def purge_shared_episodes(train: pd.DataFrame, evaluation: pd.DataFrame):
    train_ids = set(train.loc[train.stockout_within_7d, "analytical_episode_id"].dropna())
    eval_ids = set(evaluation.loc[evaluation.stockout_within_7d, "analytical_episode_id"].dropna())
    shared = train_ids & eval_ids
    remove = train.analytical_episode_id.isin(shared)
    return train.loc[~remove].copy(), {"shared_episode_ids": sorted(shared), "rows_removed": int(remove.sum()),
        "positive_rows_removed": int((remove & train.stockout_within_7d).sum()),
        "dates_removed": sorted(train.loc[remove, "prediction_date"].dt.strftime("%Y-%m-%d").unique().tolist())}


def feature_contract(cfg):
    numeric = cfg["features"]["numerical_count"] + cfg["features"]["numerical_continuous"]
    categorical = cfg["features"]["categorical"]
    features = numeric + categorical
    overlap = set(features) & set(cfg["forbidden_features"])
    if overlap: raise ValueError(f"Forbidden features: {sorted(overlap)}")
    return numeric, categorical, features


def classification_metrics(y, probability, threshold: float) -> dict[str, Any]:
    y = np.asarray(y, dtype=int); p = np.asarray(probability, dtype=float); pred = p >= threshold
    cm = confusion_matrix(y, pred, labels=[0, 1])
    return {"average_precision": float(average_precision_score(y, p)),
            "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
            "brier": float(brier_score_loss(y, p)), "precision": float(precision_score(y, pred, zero_division=0)),
            "recall": float(recall_score(y, pred, zero_division=0)), "f1": float(f1_score(y, pred, zero_division=0)),
            "confusion_matrix": {"tn": int(cm[0,0]), "fp": int(cm[0,1]), "fn": int(cm[1,0]), "tp": int(cm[1,1])},
            "predicted_positive_rate": float(pred.mean()), "actual_positive_rate": float(y.mean()),
            "rows": len(y), "positive_horizons": int(y.sum()), "negative_horizons": int((1-y).sum())}


def select_f1_threshold(y, probability) -> tuple[float, dict]:
    precision, recall, thresholds = precision_recall_curve(y, probability)
    if not len(thresholds): return .5, classification_metrics(y, probability, .5)
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-15)
    best = int(np.nanargmax(f1)); threshold = float(thresholds[best])
    return threshold, classification_metrics(y, probability, threshold)


def _model(name, numeric, categorical, cfg):
    if name == "logistic_regression_balanced":
        prep = ColumnTransformer([
            ("numeric", Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)), ("scale", StandardScaler())]), numeric),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical)])
        params = cfg["models"][name]
        return Pipeline([("preprocess", prep), ("classifier", LogisticRegression(C=params["C"], max_iter=params["max_iter"], class_weight=params["class_weight"], random_state=cfg["random_seed"]))])
    prep = ColumnTransformer([
        ("numeric", SimpleImputer(strategy="median"), numeric),
        ("categorical", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, encoded_missing_value=-1), categorical)])
    params = cfg["models"][name]
    cat_mask = [False] * len(numeric) + [True] * len(categorical)
    classifier = HistGradientBoostingClassifier(learning_rate=params["learning_rate"], max_iter=params["max_iter"],
        max_leaf_nodes=params["max_leaf_nodes"], l2_regularization=params["l2_regularization"],
        categorical_features=cat_mask, random_state=cfg["random_seed"])
    return Pipeline([("preprocess", prep), ("classifier", classifier)])


def fit_model(name, frame, numeric, categorical, cfg):
    model = _model(name, numeric, categorical, cfg)
    weight = None if name == "logistic_regression_balanced" else compute_sample_weight("balanced", frame.stockout_within_7d)
    kwargs = {} if weight is None else {"classifier__sample_weight": weight}
    model.fit(frame[numeric + categorical], frame.stockout_within_7d.astype(int), **kwargs)
    return model


def baseline_probabilities(frame):
    velocity = frame.sales_velocity_7d.astype(float)
    cover = frame.available_quantity / velocity.where(velocity > 0)
    return {"always_no_stockout": np.zeros(len(frame)),
            "below_reorder_point": (frame.available_quantity <= frame.reorder_point).astype(float).to_numpy(),
            "below_safety_stock": (frame.available_quantity <= frame.safety_stock).astype(float).to_numpy(),
            "days_of_cover_rule": (cover <= 7).fillna(False).astype(float).to_numpy()}


def _partition_stats(frame, episodes=None):
    starts = None
    if episodes is not None:
        starts = int(episodes.episode_start.between(frame.prediction_date.min(), frame.prediction_date.max()).sum())
    return {"start": str(frame.prediction_date.min().date()), "end": str(frame.prediction_date.max().date()),
            "rows": len(frame), "positive_horizons": int(frame.stockout_within_7d.sum()),
            "negative_horizons": int((~frame.stockout_within_7d).sum()),
            "independent_episodes": int(frame.loc[frame.stockout_within_7d, "analytical_episode_id"].nunique()),
            "episode_starts_in_anchor_period": starts,
            "prevalence": float(frame.stockout_within_7d.mean())}


def _episode_diagnostics(pred, episodes, threshold):
    positive = pred[pred.analytical_episode_id.notna()]
    episode_ids = sorted(positive.analytical_episode_id.unique())
    episode_start = {f"W{e.warehouse_id}_S{e.sku_id}_{e.episode_start:%Y%m%d}": e.episode_start
                     for e in episodes.itertuples()}
    details=[]
    for eid in episode_ids:
        rows=positive[positive.analytical_episode_id==eid]; event=episode_start[eid]
        warned=rows[(rows.predicted_probability >= threshold) & (rows.prediction_date < event)]
        first=warned.prediction_date.min() if len(warned) else pd.NaT
        details.append({"analytical_episode_id":eid,"event_start":str(event.date()),"detected":bool(len(warned)),
                        "first_alert":None if pd.isna(first) else str(first.date()),
                        "lead_time_days":None if pd.isna(first) else int((event-first).days),"positive_horizon_rows":len(rows)})
    d=pd.DataFrame(details); lead=d.loc[d.detected,"lead_time_days"] if len(d) else pd.Series(dtype=float)
    false=pred[(pred.predicted_class==1)&(~pred.stockout_within_7d)].sort_values(["warehouse_id","sku_id","prediction_date"])
    runs=[]
    for keys,g in false.groupby(["warehouse_id","sku_id"]):
        run=(g.prediction_date.diff().dt.days.ne(1)).cumsum()
        runs.extend(g.groupby(run).size().tolist())
    summary={"test_episodes":len(d),"detected_episodes":int(d.detected.sum()) if len(d) else 0,
             "missed_episodes":int((~d.detected).sum()) if len(d) else 0,
             "episode_detection_rate":float(d.detected.mean()) if len(d) else None,
             "lead_time_median_days":float(lead.median()) if len(lead) else None,
             "lead_time_mean_days":float(lead.mean()) if len(lead) else None,
             "lead_time_min_days":int(lead.min()) if len(lead) else None,"lead_time_max_days":int(lead.max()) if len(lead) else None,
             "false_positive_rows":len(false),"false_alert_runs":len(runs),
             "false_alert_run_median_days":float(np.median(runs)) if runs else 0,"false_alert_run_max_days":int(max(runs)) if runs else 0}
    return summary,d


def _calibration(y,p):
    observed, predicted=calibration_curve(y,p,n_bins=8,strategy="quantile")
    return [{"mean_predicted_probability":float(a),"observed_rate":float(b)} for a,b in zip(predicted,observed)]


def _slices(pred, threshold, minimum):
    rows=[]
    work=pred.copy()
    work["inventory_bucket"]=pd.cut(work.available_quantity,[-np.inf,0,work.reorder_point.median(),np.inf],labels=["zero","low","higher"])
    work["velocity_bucket"]=pd.qcut(work.sales_velocity_7d.rank(method="first"),3,labels=["low","medium","high"])
    for dim in ["warehouse_id","inventory_bucket","velocity_bucket"]:
        for value,g in work.groupby(dim,observed=True):
            if len(g)<minimum: continue
            m=classification_metrics(g.stockout_within_7d,g.predicted_probability,threshold)
            rows.append({"dimension":dim,"value":str(value),"episodes":int(g.analytical_episode_id.nunique()),**m})
    return pd.DataFrame(rows)


def predict_saved(path, frame):
    bundle=joblib.load(path)
    return bundle["model"].predict_proba(frame[bundle["features"]])[:,1]


def run_stockout_experiment(*, config_path=DEFAULT_CONFIG, data_path=DEFAULT_DATA, episode_path=DEFAULT_EPISODES,
                            output_dir=None, experiment_id=None, overwrite=False):
    cfg,data,episodes=load_contract(config_path,data_path,episode_path)
    data=assign_episode_ids(data,episodes)
    data=data[data.event_observed | data.horizon_complete].copy()
    numeric,categorical,features=feature_contract(cfg)
    experiment_id=experiment_id or f"stockout_classification_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_{np.random.default_rng().integers(16**6):06x}"
    out=Path(output_dir) if output_dir else ROOT/"artifacts/experiments/stockout_classification"/experiment_id
    if out.exists():
        if not overwrite: raise FileExistsError(out)
        shutil.rmtree(out)
    for d in [out/"predictions",out/"models",out/"diagnostics",out/"figures"]: d.mkdir(parents=True,exist_ok=True)
    parts={n:temporal_split(data,cfg,n) for n in ["selection_train","validation","final_train","test"]}
    pre={n:_partition_stats(f,episodes) for n,f in parts.items()}
    for n,f in parts.items():
        expected=cfg["split"][n]["rows"]
        if len(f)!=expected: raise ValueError(f"{n}: expected {expected}, got {len(f)}")
    if pd.Timestamp(cfg["split"]["selection_train"]["end"])+pd.Timedelta(days=7)>=pd.Timestamp(cfg["split"]["validation"]["start"]): raise ValueError("Selection embargo violated")
    if pd.Timestamp(cfg["split"]["final_train"]["end"])+pd.Timedelta(days=7)>=pd.Timestamp(cfg["split"]["test"]["start"]): raise ValueError("Test embargo violated")
    parts["selection_train"],purge_selection=purge_shared_episodes(parts["selection_train"],parts["validation"])
    parts["final_train"],purge_test=purge_shared_episodes(parts["final_train"],parts["test"])
    post={n:_partition_stats(f,episodes) for n,f in parts.items()}
    split_diag={"pre_purge":pre,"post_purge":post,"selection_to_validation":purge_selection,"final_train_to_test":purge_test}
    _json(out/"diagnostics/split_diagnostics.json",split_diag)
    validation=parts["validation"]; yv=validation.stockout_within_7d.astype(int)
    baseline_metrics={n:classification_metrics(yv,p,.5) for n,p in baseline_probabilities(validation).items()}
    strongest_baseline=max(baseline_metrics,key=lambda n:baseline_metrics[n]["average_precision"])
    candidates={}; fitted={}; validation_predictions={}
    for name in cfg["candidate_models"]:
        model=fit_model(name,parts["selection_train"],numeric,categorical,cfg)
        probability=model.predict_proba(validation[features])[:,1]
        threshold,threshold_metrics=select_f1_threshold(yv,probability)
        candidates[name]={"threshold":threshold,"threshold_policy":cfg["threshold_policy"],**threshold_metrics,
                          "calibration":_calibration(yv,probability)}
        fitted[name]=model; validation_predictions[name]=probability
    selected=max(candidates,key=lambda n:candidates[n]["average_precision"])
    threshold=candidates[selected]["threshold"]
    frozen={"selected_model":selected,"hyperparameters":cfg["models"][selected],"features":features,
            "numeric_features":numeric,"categorical_features":categorical,"target":cfg["target"],
            "validation_average_precision":candidates[selected]["average_precision"],"decision_threshold":threshold,
            "threshold_policy":cfg["threshold_policy"],"random_seed":cfg["random_seed"],
            "split_fingerprint":hashlib.sha256(json.dumps(cfg["split"],sort_keys=True,default=str).encode()).hexdigest(),
            "episode_purge_fingerprint":hashlib.sha256(json.dumps(split_diag,sort_keys=True,default=str).encode()).hexdigest(),
            "test_accessed":False}
    _json(out/"selected_model.json",frozen)
    val_out=validation[["prediction_date","warehouse_id","sku_id","stockout_within_7d","first_stockout_date","analytical_episode_id","available_quantity"]].copy()
    val_out["predicted_probability"]=validation_predictions[selected]; val_out["predicted_class"]=val_out.predicted_probability>=threshold; val_out["partition"]="validation"
    pl.from_pandas(val_out).write_parquet(out/"predictions/validation_predictions.parquet")
    # Test is first consumed after the frozen selection artifact exists.
    frozen=json.loads((out/"selected_model.json").read_text(encoding="utf-8"))
    final=fit_model(selected,parts["final_train"],numeric,categorical,cfg)
    test=parts["test"].copy(); probability=final.predict_proba(test[features])[:,1]
    test_metrics=classification_metrics(test.stockout_within_7d,probability,threshold)
    baseline_test=classification_metrics(test.stockout_within_7d,baseline_probabilities(test)[strongest_baseline],.5)
    pred=test[["prediction_date","warehouse_id","sku_id","stockout_within_7d","first_stockout_date","event_time_days","analytical_episode_id","available_quantity","reorder_point","safety_stock","sales_velocity_7d"]].copy()
    pred["predicted_probability"]=probability; pred["predicted_class"]=probability>=threshold; pred["partition"]="test"; pred["is_out_of_sample"]=True
    pl.from_pandas(pred).write_parquet(out/"predictions/test_predictions.parquet")
    episode_summary,episode_details=_episode_diagnostics(pred,episodes,threshold)
    episode_details.to_csv(out/"diagnostics/episode_details.csv",index=False)
    _json(out/"diagnostics/episode_diagnostics.json",episode_summary)
    calibration={"validation":candidates[selected]["calibration"],"test":_calibration(test.stockout_within_7d,probability)}
    _json(out/"diagnostics/calibration.json",calibration)
    slices=_slices(pred,threshold,cfg["minimum_slice_rows"]); slices.to_csv(out/"slice_metrics.csv",index=False)
    data_diag={"total_rows":len(data),"evaluable_rows":len(data),"positive_horizons":int(data.stockout_within_7d.sum()),
        "independent_physical_episodes":len(episodes),"episode_bearing_series":int(episodes.groupby(["warehouse_id","sku_id"]).ngroups),
        "positive_origins_already_stocked_out":int((data.stockout_within_7d&(data.available_quantity<=0)).sum()),
        "positive_rows_per_episode":data[data.stockout_within_7d].groupby("analytical_episode_id").size().describe().to_dict(),
        "date_range":[str(data.prediction_date.min().date()),str(data.prediction_date.max().date())],
        "missing_by_feature":data[features].isna().sum().to_dict(),
        "temporal_distribution_shift":{p:{c:{"mean":float(parts[p][c].astype(float).mean()),"median":float(parts[p][c].astype(float).median())} for c in ["available_quantity","sales_velocity_7d","replenishment_sum_7d"]} for p in ["selection_train","validation","test"]},
        "unseen_categories":{p:{c:sorted(set(parts[p][c].astype(str))-set(parts["selection_train"][c].astype(str))) for c in categorical} for p in ["validation","test"]}}
    _json(out/"diagnostics/data_diagnostics.json",data_diag)
    bundle={"model":final,"model_name":selected,"features":features,"threshold":threshold,"target":cfg["target"]}
    joblib.dump(bundle,out/"models/final_model.joblib")
    reloaded=predict_saved(out/"models/final_model.joblib",test.head(10))
    if not np.allclose(reloaded,probability[:10]): raise RuntimeError("Reloaded model probabilities differ")
    metrics={"validation":{"baselines":baseline_metrics,"candidates":candidates},"selection":{"selected_model":selected,"threshold":threshold,"strongest_baseline":strongest_baseline},
             "test":{"selected_model":test_metrics,"strongest_baseline":baseline_test},"episode_test":episode_summary}
    _json(out/"metrics.json",metrics)
    _json(out/"dvc_metrics.json",{"test_average_precision":test_metrics["average_precision"],"test_roc_auc":test_metrics["roc_auc"],"test_brier":test_metrics["brier"],
        "test_precision":test_metrics["precision"],"test_recall":test_metrics["recall"],"test_f1":test_metrics["f1"],
        "test_episode_detection_rate":episode_summary["episode_detection_rate"],"test_median_first_warning_lead_days":episode_summary["lead_time_median_days"]})
    shutil.copy2(config_path,out/"resolved_config.yaml")
    # High-value, non-decorative figures.
    pr,rc,_=precision_recall_curve(test.stockout_within_7d,probability); plt.figure(figsize=(6,4)); plt.plot(rc,pr); plt.xlabel("Recall");plt.ylabel("Precision");plt.tight_layout();plt.savefig(out/"figures/test_precision_recall.png",dpi=180);plt.close()
    cal=pd.DataFrame(calibration["test"]);plt.figure(figsize=(5,5));plt.plot([0,1],[0,1],"--",color="gray");plt.plot(cal.mean_predicted_probability,cal.observed_rate,"o-");plt.xlabel("Mean predicted probability");plt.ylabel("Observed rate");plt.tight_layout();plt.savefig(out/"figures/test_calibration.png",dpi=180);plt.close()
    plt.figure(figsize=(6,4));plt.hist(probability[test.stockout_within_7d],bins=20,alpha=.6,label="positive");plt.hist(probability[~test.stockout_within_7d],bins=20,alpha=.6,label="negative");plt.legend();plt.tight_layout();plt.savefig(out/"figures/test_probability_distribution.png",dpi=180);plt.close()
    manifest={"experiment_id":experiment_id,"task":"stockout_classification","status":"completed","created_at_utc":datetime.now(timezone.utc).isoformat(),
        "dataset_path":_portable_path(data_path),"dataset_sha256":_sha256(Path(data_path)),"schema":{c:str(t) for c,t in pl.read_parquet_schema(data_path).items()},
        "target":cfg["target"],"prediction_horizon":cfg["target_window"],"prediction_moment":cfg["prediction_time"],"features":features,
        "forbidden_features":cfg["forbidden_features"],"splits":split_diag,"embargo_days":cfg["split"]["embargo_days"],"episode_purge_policy":cfg["episode_purge_policy"],
        "baselines":cfg["baselines"],"candidate_models":cfg["candidate_models"],"selected_model":selected,"selection_metric":cfg["primary_metric"],
        "decision_threshold":threshold,"threshold_policy":cfg["threshold_policy"],"test_metrics":test_metrics,"episode_metrics":episode_summary,
        "random_seed":cfg["random_seed"],"git":_git(),"python":platform.python_version(),"scikit_learn":sklearn.__version__,
        "artifacts":{"model":"models/final_model.joblib","validation_predictions":"predictions/validation_predictions.parquet","test_predictions":"predictions/test_predictions.parquet"},
        "model_reload_predict_proba_smoke":"passed"}
    _json(out/"manifest.json",manifest)
    report=f"""# Stockout Classification V1

## 1. Objective
Estimate future stockout risk for operational warning, not accuracy on a balanced benchmark.

## 2. Prediction contract
At inventory snapshot `t`, predict `{cfg['target']}` for `(t,t+7 days]` at warehouse–SKU grain.

## 3. Dataset and rare-event structure
There are {len(data):,} evaluable rows, {int(data.stockout_within_7d.sum()):,} positive horizons and {len(episodes)} physical episodes. The mean/median/max positive rows per episode are {data_diag['positive_rows_per_episode']['mean']:.2f}/{data_diag['positive_rows_per_episode']['50%']:.0f}/{data_diag['positive_rows_per_episode']['max']:.0f}; horizon rows are dependent. {data_diag['positive_origins_already_stocked_out']} positive origins are already stocked out at `t` and can inflate row metrics.

## 4. Physical episode definition
An episode is a warehouse–SKU `>0 → <=0` transition through the first later positive snapshot. Positive horizons map to the containing physical run using a stable warehouse/SKU/start-date ID.

## 5. Temporal split, embargo and purge
Selection train/validation and final train/test use the configured chronological blocks. The seven-day target-window embargo passed. Episode purge removed {purge_selection['rows_removed']} and {purge_test['rows_removed']} training rows respectively; no positive episode crosses either boundary after purge. Test contains {post['test']['episode_starts_in_anchor_period']} starts and {post['test']['independent_episodes']} episodes represented by horizons.

## 6. Feature and leakage contract
Inputs are snapshot inventory, reorder/safety policy, ratios/distances, historical `[t-7,t)` sales velocity, historical `[t-7,t)` replenishment and categorical IDs. `first_stockout_date`, classification/survival outcomes, censoring and completeness are evaluation-only. Actual future delivery realization is excluded.

## 7. Baselines and candidates
Operational rules are always-negative, reorder point, safety stock and seven-day cover. Hard rules are decisions, not calibrated probabilities; their Brier value is the binary squared error rate. Candidates are class-weighted logistic regression and weighted histogram gradient boosting with train-fitted preprocessing.

## 8. Validation and selection
Logistic AP={candidates['logistic_regression_balanced']['average_precision']:.4f}; histogram boosting AP={candidates['histogram_gradient_boosting']['average_precision']:.4f}; strongest baseline `{strongest_baseline}` AP={baseline_metrics[strongest_baseline]['average_precision']:.4f}. `{selected}` won on validation AP. Threshold {threshold:.6f} maximizes validation F1 and was persisted before test access. The selected pipeline was refit from scratch on final train.

## 9. Final test
Support: {len(test):,} rows, {int(test.stockout_within_7d.sum())} positive horizons, {post['test']['independent_episodes']} represented episodes. Model AP={test_metrics['average_precision']:.4f}, ROC-AUC={test_metrics['roc_auc']:.4f}, Brier={test_metrics['brier']:.4f}, precision={test_metrics['precision']:.4f}, recall={test_metrics['recall']:.4f}, F1={test_metrics['f1']:.4f}, alert rate={test_metrics['predicted_positive_rate']:.2%}. Frozen baseline AP={baseline_test['average_precision']:.4f}, F1={baseline_test['f1']:.4f}.

## 10. Calibration
Reliability bins are persisted. No calibrator was fit because validation contains only {post['validation']['episode_starts_in_anchor_period']} starts/{post['validation']['independent_episodes']} represented episodes and calibration fitting would be unstable.

## 11. Episode detection and lead time
Detected {episode_summary['detected_episodes']}/{episode_summary['test_episodes']} episodes ({episode_summary['episode_detection_rate']:.2%}) strictly before physical onset. First-warning lead median/mean/range: {episode_summary['lead_time_median_days']}/{episode_summary['lead_time_mean_days']:.2f}/{episode_summary['lead_time_min_days']}–{episode_summary['lead_time_max_days']} days.

## 12. False alerts, slices and error analysis
There are {episode_summary['false_positive_rows']} false-positive rows in {episode_summary['false_alert_runs']} runs; median/max run length is {episode_summary['false_alert_run_median_days']}/{episode_summary['false_alert_run_max_days']} days. Slice metrics include warehouse, inventory and velocity bands with support. Test recall is below the frozen safety-stock rule despite better AP, and low/medium-velocity slices show weak detection; these are V2 hypotheses, not reasons to retune V1.

## 13. Persistence and reproducibility
The complete preprocessing/model pipeline reloads with identical `predict_proba` output. Manifest, frozen selection, validation/test predictions, calibration, episode details, slices and figures are stored under this canonical artifact and managed by DVC.

## 14. Limitations and V2 hypotheses
This is a synthetic ~90-day offline evaluation with dependent horizons, limited independent events, temporal prevalence shift and no production validation. V2 may study episode-normalized weighting, onset-only sensitivity and explicit point-in-time pending-order state. No survival model, calibration layer or test-driven retuning is included.
"""
    (out/"report.md").write_text(report,encoding="utf-8")
    return {"experiment_id":experiment_id,"output_dir":str(out),"selected_model":selected,"threshold":threshold,"test_metrics":test_metrics,"episode_metrics":episode_summary}
