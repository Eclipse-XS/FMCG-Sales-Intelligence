from __future__ import annotations

import json
import platform
import shutil
import subprocess
from dataclasses import dataclass
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
from catboost import CatBoostRegressor
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import PoissonRegressor, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .metrics import nonnegative, regression_metrics

ROOT = Path(__file__).resolve().parents[2]


def _portable_path(path: Path | str) -> str:
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()
DEFAULT_CONFIG = ROOT / "configs/modeling/forecasting.yaml"
DEFAULT_DATA = ROOT / "data/processed/forecasting/forecasting_v1.parquet"


@dataclass(frozen=True)
class ExperimentResult:
    experiment_id: str
    output_dir: Path
    selected_model: str
    validation_metrics: dict[str, Any]
    test_metrics: dict[str, float]


def _git_info() -> dict[str, Any]:
    def run(*args):
        result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
        return result.stdout.strip() if result.returncode == 0 else None
    return {"commit": run("rev-parse", "HEAD"), "branch": run("branch", "--show-current"),
            "dirty": bool(run("status", "--porcelain"))}


def _load(config_path: Path, data_path: Path):
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    df = pl.read_parquet(data_path).to_pandas()
    df["prediction_date"] = pd.to_datetime(df["prediction_date"])
    return cfg, df


def _columns(cfg):
    numeric = cfg["features"]["numerical_count"] + cfg["features"]["numerical_continuous"]
    categorical = cfg["features"]["categorical"]
    features = numeric + categorical
    forbidden = set(cfg["forbidden_features"])
    if forbidden.intersection(features):
        raise ValueError(f"Forbidden target fields in features: {forbidden.intersection(features)}")
    return numeric, categorical, features


def _split(df, spec):
    start, end = pd.Timestamp(spec["start"]), pd.Timestamp(spec["end"])
    return df[df.prediction_date.between(start, end)].copy()


def _sklearn_model(name, numeric, categorical):
    prep = ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                              ("scale", StandardScaler())]), numeric),
        ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                  ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    reg = Ridge(alpha=1.0) if name == "ridge" else PoissonRegressor(alpha=1.0, max_iter=500)
    return Pipeline([("preprocess", prep), ("regressor", reg)])


def _cat_frame(df, features, categorical):
    x = df[features].copy()
    for col in categorical:
        x[col] = x[col].fillna("__MISSING__").astype(str)
    return x


def _fit(name, train, features, numeric, categorical, seed):
    y = train.target_units_next_7d.to_numpy()
    if name == "catboost_regressor":
        model = CatBoostRegressor(iterations=300, depth=7, learning_rate=.05, loss_function="RMSE",
                                  random_seed=seed, verbose=False, allow_writing_files=False, thread_count=4)
        model.fit(_cat_frame(train, features, categorical), y, cat_features=categorical)
    else:
        model = _sklearn_model(name, numeric, categorical)
        model.fit(train[features], y)
    return model


def _predict(model, name, frame, features, categorical):
    x = _cat_frame(frame, features, categorical) if name == "catboost_regressor" else frame[features]
    return nonnegative(model.predict(x))


def _baselines(frame):
    velocity = frame.sales_velocity_7d.fillna(0).to_numpy(float)
    return {"zero": np.zeros(len(frame)), "last_value_7x": 7 * frame.lag_1.fillna(0).to_numpy(float),
            "trailing_7_day_sum": velocity, "prior_week_sum": velocity.copy()}


def _diagnostics(train, other, categorical):
    unseen = {}
    for col in categorical:
        known, values = set(train[col].dropna().astype(str)), set(other[col].dropna().astype(str))
        unseen[col] = sorted(values - known)
    return {"rows": len(other), "target_zero_rate": float((other.target_units_next_7d == 0).mean()),
            "feature_null_counts": other.isna().sum().loc[lambda s: s > 0].to_dict(), "unseen_categories": unseen}


def _selection(train, validation, cfg, features, numeric, categorical):
    y = validation.target_units_next_7d
    baseline = {n: regression_metrics(y, p) for n, p in _baselines(validation).items()}
    candidates, fitted = {}, {}
    for name in cfg["candidate_models"]:
        try:
            model = _fit(name, train, features, numeric, categorical, cfg["random_seed"])
            pred = _predict(model, name, validation, features, categorical)
            candidates[name] = {"status": "ok", **regression_metrics(y, pred)}
            fitted[name] = model
        except Exception as exc:
            candidates[name] = {"status": "skipped", "reason": f"{type(exc).__name__}: {exc}"}
    eligible = [n for n, m in candidates.items() if m["status"] == "ok"]
    if not eligible:
        raise RuntimeError("No candidate model completed selection")
    best = min(eligible, key=lambda n: candidates[n]["wape"])
    # Within 0.5% relative WAPE, prefer the simpler deployable candidate.
    order = {"ridge": 0, "poisson_regressor": 1, "catboost_regressor": 2}
    threshold = candidates[best]["wape"] * 1.005
    selected = min((n for n in eligible if candidates[n]["wape"] <= threshold), key=lambda n: order[n])
    return selected, {"baselines": baseline, "candidates": candidates,
                      "selection_rule": "minimum validation WAPE; within 0.5% relative WAPE prefer Ridge, then Poisson, then CatBoost"}


def _slice_table(pred):
    rows = []
    dimensions = ["store_id", "sku_id", "category_name", "channel", "scheduled_is_promo",
                  "demand_volume_group", "intermittent_group", "inventory_censored_context"]
    for dimension in dimensions:
        for value, group in pred.groupby(dimension, dropna=False):
            rows.append({"dimension": dimension, "value": str(value), "support": len(group),
                         **regression_metrics(group.actual, group.prediction)})
    return pd.DataFrame(rows)


def _add_context(final_train, test):
    history = final_train.groupby(["store_id", "sku_id"]).agg(
        mean_lag=("lag_1", "mean"), zero_rate=("lag_1", lambda s: float((s.fillna(0) == 0).mean())))
    q1, q2 = history.mean_lag.quantile([.33, .67])
    history["demand_volume_group"] = pd.cut(history.mean_lag, [-np.inf, q1, q2, np.inf], labels=["low", "medium", "high"]).astype(str)
    history["intermittent_group"] = np.where(history.zero_rate >= .5, "intermittent", "regular")
    result = test.merge(history[["demand_volume_group", "intermittent_group"]], left_on=["store_id", "sku_id"], right_index=True, how="left")
    result["inventory_censored_context"] = np.where(result.target_lost_sales_next_7d > 0, "censored", "not_censored")
    return result


def _figures(pred, slice_df, output):
    output.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4)); pred.actual.hist(bins=50, alpha=.6, label="actual"); pred.prediction.hist(bins=50, alpha=.6, label="prediction"); plt.legend(); plt.tight_layout(); plt.savefig(output / "prediction_distribution.png", dpi=180); plt.close()
    daily = pred.groupby("prediction_date")[["actual", "prediction"]].sum()
    daily.plot(figsize=(9, 4)); plt.tight_layout(); plt.savefig(output / "aggregate_time_series.png", dpi=180); plt.close()
    plt.figure(figsize=(6, 5)); plt.scatter(pred.actual, pred.prediction, s=3, alpha=.15); lim=max(pred.actual.max(), pred.prediction.max()); plt.plot([0,lim],[0,lim], color="black"); plt.xlabel("actual"); plt.ylabel("prediction"); plt.tight_layout(); plt.savefig(output / "actual_vs_predicted.png", dpi=180); plt.close()
    top = slice_df[slice_df.dimension == "category_name"].sort_values("wape")
    plt.figure(figsize=(8, 4)); plt.bar(top.value, top.wape); plt.xticks(rotation=35, ha="right"); plt.ylabel("WAPE"); plt.tight_layout(); plt.savefig(output / "category_wape.png", dpi=180); plt.close()


def predict_saved(model_path: Path | str, frame: pd.DataFrame) -> np.ndarray:
    bundle = joblib.load(model_path)
    return _predict(bundle["model"], bundle["model_name"], frame, bundle["features"], bundle["categorical"])


def run_experiment(*, config_path: Path | str = DEFAULT_CONFIG, data_path: Path | str = DEFAULT_DATA,
                   output_dir: Path | str | None = None, experiment_id: str | None = None,
                   overwrite: bool = False) -> ExperimentResult:
    config_path, data_path = Path(config_path), Path(data_path)
    now = datetime.now(timezone.utc)
    experiment_id = experiment_id or f"forecasting_{now:%Y%m%dT%H%M%SZ}_{np.random.default_rng().integers(0, 16**6):06x}"
    out = Path(output_dir) if output_dir else ROOT / "artifacts/experiments/forecasting" / experiment_id
    if out.exists():
        if not overwrite: raise FileExistsError(out)
        shutil.rmtree(out)
    for d in [out / "predictions", out / "models", out / "figures", out / "diagnostics"]: d.mkdir(parents=True, exist_ok=True)
    cfg, df = _load(config_path, data_path)
    numeric, categorical, features = _columns(cfg)
    required = set(features + cfg["identifiers"] + [cfg["primary_target"], "target_lost_sales_next_7d"])
    missing = required - set(df.columns)
    if missing: raise ValueError(f"Missing required columns: {sorted(missing)}")
    parts = {name: _split(df, cfg["split"][name]) for name in ["selection_train", "validation", "final_train", "test"]}
    for name, frame in parts.items():
        if len(frame) != cfg["split"][name]["rows"]: raise ValueError(f"{name} row count: {len(frame)}")
    selected, validation_metrics = _selection(parts["selection_train"], parts["validation"], cfg, features, numeric, categorical)
    selection_spec = {"selected_model": selected, "selected_at": now.isoformat(), "features": features,
                      "target": cfg["primary_target"], "selection_partition": "validation", "test_accessed": False}
    (out / "selected_model.json").write_text(json.dumps(selection_spec, indent=2), encoding="utf-8")
    # Test data is first consumed only after the immutable selection record above exists.
    frozen = json.loads((out / "selected_model.json").read_text(encoding="utf-8"))
    final_model = _fit(frozen["selected_model"], parts["final_train"], features, numeric, categorical, cfg["random_seed"])
    test = _add_context(parts["final_train"], parts["test"])
    raw = final_model.predict(_cat_frame(test, features, categorical) if selected == "catboost_regressor" else test[features])
    clipped = nonnegative(raw)
    test_metrics = regression_metrics(test.target_units_next_7d, clipped)
    strongest_baseline = min(validation_metrics["baselines"], key=lambda n: validation_metrics["baselines"][n]["wape"])
    baseline_test = regression_metrics(test.target_units_next_7d, _baselines(test)[strongest_baseline])
    pred = test[["prediction_date", "store_id", "sku_id", "category_name", "channel", "scheduled_is_promo", "demand_volume_group", "intermittent_group", "inventory_censored_context"]].copy()
    pred["actual"], pred["raw_prediction"], pred["prediction"] = test.target_units_next_7d.to_numpy(dtype=float), raw, clipped
    pred["residual"], pred["model_name"], pred["partition"], pred["is_out_of_sample"] = pred.actual-pred.prediction, selected, "test", True
    pl.from_pandas(pred).write_parquet(out / "predictions/test_predictions.parquet")
    bundle = {"model": final_model, "model_name": selected, "features": features, "categorical": categorical,
              "target": cfg["primary_target"], "clip_lower": 0.0}
    joblib.dump(bundle, out / "models/final_model.joblib")
    # Loading and inference smoke test protects deployability of the persisted artifact.
    smoke = predict_saved(out / "models/final_model.joblib", test.head(3))
    if len(smoke) != 3 or not np.isfinite(smoke).all(): raise RuntimeError("Persisted model smoke test failed")
    slices = _slice_table(pred); slices.to_csv(out / "slice_metrics.csv", index=False)
    diagnostics = {n: _diagnostics(parts["selection_train"], p, categorical) for n, p in parts.items()}
    (out / "diagnostics/data_diagnostics.json").write_text(json.dumps(diagnostics, indent=2, default=str), encoding="utf-8")
    _figures(pred, slices, out / "figures")
    all_metrics = {"validation": validation_metrics, "test": {selected: test_metrics, strongest_baseline: baseline_test},
                   "selected_model": selected, "strongest_baseline": strongest_baseline,
                   "test_evaluations_performed": 1}
    (out / "metrics.json").write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")
    (out / "dvc_metrics.json").write_text(json.dumps({"test_wape": test_metrics["wape"], "test_mae": test_metrics["mae"], "test_rmse": test_metrics["rmse"], "test_signed_bias": test_metrics["signed_bias"]}, indent=2), encoding="utf-8")
    shutil.copy2(config_path, out / "resolved_config.yaml")
    manifest = {"experiment_id": experiment_id, "created_at_utc": now.isoformat(), "task": "forecasting",
                "data_path": _portable_path(data_path), "data_rows": len(df), "data_columns": list(df.columns),
                "splits": {n: {"rows": len(p), "start": str(p.prediction_date.min().date()), "end": str(p.prediction_date.max().date())} for n,p in parts.items()},
                "features": features, "excluded_optional_features": cfg["features"]["optional_experimental"],
                "target": cfg["primary_target"], "git": _git_info(), "python": platform.python_version(),
                "packages": {"scikit-learn": sklearn.__version__, "catboost": __import__("catboost").__version__, "polars": pl.__version__},
                "random_seed": cfg["random_seed"], "prediction_semantics": "start of day t; features are pre-event; target is demand in (t,t+7]",
                "postprocessing": "clip predictions at zero", "persisted_model_smoke_test": "passed"}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    improvement = 1 - test_metrics["wape"] / baseline_test["wape"]
    report = f"""# Forecasting experiment {experiment_id}\n\n## Decision\n\nSelected `{selected}` using validation WAPE only. The selection was written to `selected_model.json` before test access. The final model was refit from scratch on the approved final-training interval and test was evaluated once.\n\n## Test result\n\n- Model WAPE: {test_metrics['wape']:.6f}\n- Model MAE: {test_metrics['mae']:.6f}\n- Model RMSE: {test_metrics['rmse']:.6f}\n- Model signed bias: {test_metrics['signed_bias']:.6f}\n- Strongest validation baseline: `{strongest_baseline}`; test WAPE: {baseline_test['wape']:.6f}\n- Relative WAPE improvement: {improvement:.2%}\n\nSigned bias is `sum(prediction-actual)/sum(abs(actual))`; negative means under-forecasting. Predictions are clipped at zero.\n\n## Scope and limitations\n\nThis synthetic development dataset covers one short seasonal interval. Optional `scheduled_is_promo` and `censored_days_prior_7d` were excluded from V1 model features because the former is constant in the current artifact and the latter is an optional censoring signal. Inventory censoring is used only as post-hoc evaluation context. Results do not establish production generalization.\n"""
    (out / "report.md").write_text(report, encoding="utf-8")
    return ExperimentResult(experiment_id, out, selected, validation_metrics, test_metrics)
