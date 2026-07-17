"""Leakage-safe modeling experiments."""

from .forecasting import ExperimentResult, run_experiment as run_forecasting_experiment
from .stockout import run_stockout_experiment
from .survival import run_survival_experiment
from .segmentation import run_segmentation_experiment
from .anomaly import run_anomaly_experiment
from .basket import run_basket_experiment
from .promotion import run_promotion_experiment


def run_experiment(task: str = "forecasting", **kwargs):
    if task == "forecasting":
        return run_forecasting_experiment(**kwargs)
    if task == "stockout_classification":
        return run_stockout_experiment(**kwargs)
    if task == "stockout_survival":
        return run_survival_experiment(**kwargs)
    if task == "segmentation":
        return run_segmentation_experiment(**kwargs)
    if task == "anomaly":
        return run_anomaly_experiment(**kwargs)
    if task == "basket":
        return run_basket_experiment(**kwargs)
    if task == "promotion":
        return run_promotion_experiment(**kwargs)
    raise ValueError(f"Unsupported modeling task: {task}")


__all__ = ["ExperimentResult", "run_experiment", "run_forecasting_experiment", "run_stockout_experiment", "run_survival_experiment", "run_segmentation_experiment", "run_anomaly_experiment", "run_basket_experiment", "run_promotion_experiment"]
