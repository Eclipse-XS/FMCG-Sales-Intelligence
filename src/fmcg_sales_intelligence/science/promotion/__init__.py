"""Public API for the promotion scientific core."""

from .experiment import (
    DEFAULT_CONFIG,
    DEFAULT_DAILY,
    DEFAULT_EXPOSURE,
    build_exposure_metrics,
    load_data,
    promotion_summary,
    run_promotion_experiment,
    sensitivity,
    validate_contract,
)

__all__ = [
    "DEFAULT_CONFIG",
    "DEFAULT_DAILY",
    "DEFAULT_EXPOSURE",
    "build_exposure_metrics",
    "load_data",
    "promotion_summary",
    "run_promotion_experiment",
    "sensitivity",
    "validate_contract",
]
