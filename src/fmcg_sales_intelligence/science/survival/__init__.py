"""Public API for the stockout survival scientific core."""

from .experiment import (
    CLASSIFICATION_CONFIG,
    DEFAULT_CONFIG,
    DEFAULT_DATA,
    DEFAULT_EPISODES,
    build_survival_cohort,
    fit_cox,
    horizon_metrics,
    km_summary,
    ph_diagnostics,
    predict_bundle,
    purge_shared_survival_events,
    run_survival_experiment,
    survival_c_index,
    survival_feature_contract,
)

__all__ = [
    "CLASSIFICATION_CONFIG",
    "DEFAULT_CONFIG",
    "DEFAULT_DATA",
    "DEFAULT_EPISODES",
    "build_survival_cohort",
    "fit_cox",
    "horizon_metrics",
    "km_summary",
    "ph_diagnostics",
    "predict_bundle",
    "purge_shared_survival_events",
    "run_survival_experiment",
    "survival_c_index",
    "survival_feature_contract",
]
