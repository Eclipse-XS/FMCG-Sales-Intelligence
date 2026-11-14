from __future__ import annotations

import numpy as np


def regression_metrics(actual, prediction) -> dict[str, float]:
    """Score paired, finite observations; reject accidental NumPy broadcasting."""
    y = np.asarray(actual, dtype=float)
    p = np.asarray(prediction, dtype=float)
    if y.ndim != 1 or p.ndim != 1 or y.shape != p.shape:
        raise ValueError("actual and prediction must be one-dimensional arrays of equal length")
    if y.size == 0:
        raise ValueError("actual and prediction must contain at least one observation")
    if not np.isfinite(y).all() or not np.isfinite(p).all():
        raise ValueError("actual and prediction must contain only finite values")
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
