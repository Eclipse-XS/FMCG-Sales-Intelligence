from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

from .registry import FrozenModelRegistry


FORBIDDEN_FORECAST = {
    "observed_units",
    "target_units_next_7d",
    "target_requested_demand_next_7d",
    "target_lost_sales_next_7d",
    "realized_transaction_unit_price",
}
FORBIDDEN_STOCKOUT = {
    "first_stockout_date",
    "stockout_within_7d",
    "event_observed",
    "event_time_days",
    "censor_time_days",
    "horizon_complete",
}


def _validate_rows(rows: list[dict[str, Any]], features: list[str], forbidden: set[str]) -> pd.DataFrame:
    if not rows or len(rows) > 1000:
        raise ValueError("Batch size must be between 1 and 1000")
    supplied = set().union(*(row.keys() for row in rows))
    blocked = supplied & forbidden
    if blocked:
        raise ValueError(f"Forbidden outcome/future fields: {sorted(blocked)}")
    missing = set(features) - supplied
    if missing:
        raise ValueError(f"Missing required features: {sorted(missing)}")
    frame = pd.DataFrame(rows)
    numeric = frame[features].select_dtypes(include=["number"])
    if not numeric.empty and np.isinf(numeric.to_numpy(dtype=float)).any():
        raise ValueError("Infinite feature values are not accepted")
    return frame[features].copy()


class ForecastService:
    def __init__(self, registry: FrozenModelRegistry):
        self.record = registry.get("forecasting")

    def predict(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.record.ready:
            raise RuntimeError("Forecast model unavailable")
        bundle = self.record.bundle
        features, categorical = bundle["features"], bundle["categorical"]
        frame = _validate_rows(rows, features, FORBIDDEN_FORECAST)
        for column in categorical:
            frame[column] = frame[column].fillna("__MISSING__").astype(str)
        predictions = np.maximum(bundle["model"].predict(frame), float(bundle.get("clip_lower", 0)))
        now = datetime.now(timezone.utc).isoformat()
        return [
            {
                "model": "forecasting",
                "model_version": self.record.version,
                "prediction_timestamp": now,
                "prediction_target": bundle["target"],
                "prediction_horizon": "(t,t+7d]",
                "predicted_units": float(value),
                "nonnegative_clipping": True,
            }
            for value in predictions
        ]


class StockoutService:
    def __init__(self, registry: FrozenModelRegistry):
        self.record = registry.get("stockout_classification")

    def predict(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.record.ready:
            raise RuntimeError("Stockout model unavailable")
        bundle = self.record.bundle
        frame = _validate_rows(rows, bundle["features"], FORBIDDEN_STOCKOUT)
        probabilities = bundle["model"].predict_proba(frame)[:, 1]
        threshold = float(bundle["threshold"])
        now = datetime.now(timezone.utc).isoformat()
        return [
            {
                "model": "stockout_classification",
                "model_version": self.record.version,
                "prediction_timestamp": now,
                "prediction_target": "stockout occurrence within (t,t+7d]",
                "prediction_horizon": "(t,t+7d]",
                "stockout_probability": float(value),
                "decision_threshold": threshold,
                "risk_flag": bool(value >= threshold),
                "calibration_note": "Score is not claimed to be strongly calibrated.",
            }
            for value in probabilities
        ]
