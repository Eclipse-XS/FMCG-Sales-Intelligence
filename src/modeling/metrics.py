from __future__ import annotations

import numpy as np


def regression_metrics(actual, prediction) -> dict[str, float]:
    y = np.asarray(actual, dtype=float)
    p = np.asarray(prediction, dtype=float)
    error = p - y
    denominator = float(np.abs(y).sum())
    return {
        "wape": float(np.abs(error).sum() / denominator) if denominator else float("nan"),
        "mae": float(np.abs(error).mean()),
        "rmse": float(np.sqrt(np.square(error).mean())),
        "signed_bias": float(error.sum() / denominator) if denominator else float("nan"),
    }


def nonnegative(prediction):
    return np.maximum(np.asarray(prediction, dtype=float), 0.0)
