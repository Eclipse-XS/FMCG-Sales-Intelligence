"""Public API for the segmentation scientific core."""

from .experiment import (
    DEFAULT_CONFIG,
    DEFAULT_DATA,
    audit_features,
    canonicalize,
    evaluate_candidates,
    load_contract,
    nearest_centroid,
    run_segmentation_experiment,
    select_latest_snapshot,
)

__all__ = [
    "DEFAULT_CONFIG",
    "DEFAULT_DATA",
    "audit_features",
    "canonicalize",
    "evaluate_candidates",
    "load_contract",
    "nearest_centroid",
    "run_segmentation_experiment",
    "select_latest_snapshot",
]
