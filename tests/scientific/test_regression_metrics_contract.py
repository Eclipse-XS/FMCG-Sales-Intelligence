import numpy as np
import pytest

from fmcg_sales_intelligence.science.metrics import regression_metrics


@pytest.mark.parametrize("actual,prediction", [
    ([1, 3], [[2], [1]]),
    ([1, 3], [2]),
    (1, 2),
    ([], []),
    ([1, np.nan], [2, 1]),
    ([1, 3], [np.inf, 1]),
])
def test_invalid_observations_are_rejected(actual, prediction):
    with pytest.raises(ValueError):
        regression_metrics(actual, prediction)


def test_paired_observations_preserve_metric_definitions():
    result = regression_metrics([1, 3], [2, 1])
    assert result == pytest.approx({
        "wape": .75, "mae": 1.5, "rmse": np.sqrt(2.5), "signed_bias": -.25,
    })


def test_zero_total_actual_keeps_normalized_metrics_undefined():
    result = regression_metrics([0, 0], [1, 2])
    assert np.isnan(result["wape"])
    assert np.isnan(result["signed_bias"])
    assert result["mae"] == 1.5
