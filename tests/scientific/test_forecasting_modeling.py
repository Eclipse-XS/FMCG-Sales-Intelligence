from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from fmcg_sales_intelligence.science.forecasting import DEFAULT_CONFIG, _baselines, _columns, _split
from fmcg_sales_intelligence.science.metrics import nonnegative, regression_metrics


def test_metric_definitions():
    metrics = regression_metrics([1, 3], [2, 1])
    assert metrics["wape"] == .75
    assert metrics["mae"] == 1.5
    assert metrics["signed_bias"] == -.25


def test_predictions_are_clipped_nonnegative():
    assert nonnegative([-2, 1]).tolist() == [0, 1]


def test_feature_contract_excludes_targets_and_optional_features():
    cfg = yaml.safe_load(Path(DEFAULT_CONFIG).read_text(encoding="utf-8"))
    _, _, features = _columns(cfg)
    assert not set(features).intersection(cfg["forbidden_features"])
    assert not set(features).intersection(cfg["features"]["optional_experimental"])


def test_split_boundaries_are_inclusive_and_disjoint():
    cfg = yaml.safe_load(Path(DEFAULT_CONFIG).read_text(encoding="utf-8"))
    dates = pd.date_range("2024-01-01", "2024-03-23")
    df = pd.DataFrame({"prediction_date": dates})
    parts = {n: _split(df, cfg["split"][n]) for n in ["selection_train", "validation", "final_train", "test"]}
    assert parts["selection_train"].prediction_date.max() < parts["validation"].prediction_date.min()
    assert parts["final_train"].prediction_date.max() < parts["test"].prediction_date.min()
    assert (parts["validation"].prediction_date.min() - parts["selection_train"].prediction_date.max()).days == 8


def test_baselines_have_expected_semantics():
    frame = pd.DataFrame({"lag_1": [2, np.nan], "sales_velocity_7d": [9, 4]})
    result = _baselines(frame)
    assert result["zero"].tolist() == [0, 0]
    assert result["last_value_7x"].tolist() == [14, 0]
    assert result["trailing_7_day_sum"].tolist() == [9, 4]
    assert np.array_equal(result["trailing_7_day_sum"], result["prior_week_sum"])
