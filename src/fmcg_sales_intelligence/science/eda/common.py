from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT

import json
import math
from pathlib import Path
from typing import Any

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

ROOT = PROJECT_ROOT
WAREHOUSE = ROOT / "data/warehouse/fmcg.duckdb"
PROCESSED = ROOT / "data/processed"
REPORT = ROOT / "artifacts/reports/eda"
FIGURES = REPORT / "figures"

ARTIFACTS = ["forecasting", "stockout", "segmentation", "segment_assignment", "anomaly", "basket", "promotion_performance"]
KEYS = {
    "forecasting": ["prediction_date", "store_id", "sku_id"],
    "stockout": ["prediction_date", "warehouse_id", "sku_id"],
    "segmentation": ["snapshot_date", "store_id"],
    "segment_assignment": ["snapshot_date", "store_id"],
    "anomaly": ["event_date", "store_id", "sku_id"],
    "basket": ["order_id", "sku_id"],
    "promotion_performance": ["promotion_id", "store_id", "sku_id"],
}
DATES = {"forecasting": "prediction_date", "stockout": "prediction_date", "segmentation": "snapshot_date", "segment_assignment": "snapshot_date", "anomaly": "event_date", "basket": "order_date", "promotion_performance": "start_date"}
TARGETS = {
    "forecasting": ["target_units_next_7d", "target_observed_next_7d"],
    "stockout": ["stockout_within_7d", "event_observed", "event_time_days", "censor_time_days", "horizon_complete"],
    "segmentation": [], "segment_assignment": [], "anomaly": [], "basket": [], "promotion_performance": [],
}
IDENTIFIERS = {"store_id", "sku_id", "warehouse_id", "promotion_id", "scheduled_promotion_id", "order_id", "region_id"}


def load(name: str) -> pl.DataFrame:
    return pl.read_parquet(PROCESSED / name / f"{name}_v1.parquet")


def query(statement: str, params: list[Any] | None = None) -> pl.DataFrame:
    with duckdb.connect(str(WAREHOUSE), read_only=True) as conn:
        return pl.from_arrow(conn.execute(statement, params or []).arrow())


def output_dir(name: str) -> Path:
    path = REPORT / name
    path.mkdir(parents=True, exist_ok=True)
    (FIGURES / name).mkdir(parents=True, exist_ok=True)
    return path


def save_json(name: str, payload: dict[str, Any]) -> None:
    def clean(value):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items()}
        if isinstance(value, list):
            return [clean(item) for item in value]
        return value
    path = output_dir(name) / "metrics.json"
    path.write_text(json.dumps(clean(payload), indent=2, default=str, allow_nan=False), encoding="utf-8")


def save_report(name: str, lines: list[str]) -> None:
    (output_dir(name) / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def savefig(name: str, filename: str) -> str:
    plt.tight_layout()
    path = FIGURES / name / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    return str(path.relative_to(REPORT)).replace("\\", "/")


def numeric_summary(frame: pl.DataFrame, columns: list[str]) -> dict[str, dict[str, float | int | None]]:
    result: dict[str, dict[str, float | int | None]] = {}
    for column in columns:
        series = frame[column].cast(pl.Float64, strict=False).drop_nulls()
        if not len(series):
            result[column] = {"count": 0, "mean": None, "median": None, "std": None, "min": None, "p25": None, "p75": None, "p95": None, "max": None}
            continue
        values = series.to_numpy()
        result[column] = {
            "count": len(values), "mean": float(np.mean(values)), "median": float(np.median(values)),
            "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0, "min": float(np.min(values)),
            "p25": float(np.quantile(values, .25)), "p75": float(np.quantile(values, .75)),
            "p95": float(np.quantile(values, .95)), "max": float(np.max(values)),
        }
    return result


def overview() -> dict[str, Any]:
    result = {}
    for name in ARTIFACTS:
        frame = load(name)
        date_col = DATES[name]
        categoricals = [c for c, t in zip(frame.columns, frame.dtypes) if t == pl.String]
        binaries = [c for c, t in zip(frame.columns, frame.dtypes) if t == pl.Boolean]
        numerics = [c for c, t in zip(frame.columns, frame.dtypes) if t.is_numeric() and c not in IDENTIFIERS]
        result[name] = {
            "path": str((PROCESSED / name / f"{name}_v1.parquet").relative_to(ROOT)).replace("\\", "/"),
            "rows": frame.height, "columns": frame.width, "grain": KEYS[name], "targets": TARGETS[name],
            "date_column": date_col, "date_range": [str(frame[date_col].min()), str(frame[date_col].max())],
            "numerical": numerics, "categorical": categoricals, "binary": binaries,
            "temporal": [c for c, t in zip(frame.columns, frame.dtypes) if t in (pl.Date, pl.Datetime)],
            "identifiers": [c for c in frame.columns if c in IDENTIFIERS],
            "null_rates": {c: frame[c].null_count() / frame.height for c in frame.columns},
            "categorical_cardinality": {c: frame[c].n_unique() for c in categoricals},
            "duplicate_business_keys": int(frame.select(KEYS[name]).is_duplicated().sum()),
            "schema": {c: str(t) for c, t in zip(frame.columns, frame.dtypes)},
        }
    return result
