from __future__ import annotations

import pandas as pd
import polars as pl
from decimal import Decimal
from fastapi.testclient import TestClient

from fmcg_sales_intelligence.product.api.app import create_app
from fmcg_sales_intelligence.product.serving import ForecastService, FrozenModelRegistry, StockoutService


def _row(path, features):
    row = pl.read_parquet(path).select(features).drop_nulls().head(1).to_pandas().iloc[0].to_dict()
    return {
        key: float(value) if isinstance(value, Decimal) else value.item() if hasattr(value, "item") else value
        for key, value in row.items()
    }


def test_frozen_registry_loads_trusted_bundles():
    registry = FrozenModelRegistry()
    assert registry.ready
    assert all(x["load_test"] == "PASS" for x in registry.serialization_catalog())


def test_forecast_service_matches_canonical_model_and_clips_nonnegative():
    registry = FrozenModelRegistry()
    record = registry.get("forecasting")
    row = _row("data/processed/forecasting/forecasting_v1.parquet", record.bundle["features"])
    result = ForecastService(registry).predict([row])[0]
    frame = pd.DataFrame([row])
    for column in record.bundle["categorical"]:
        frame[column] = frame[column].fillna("__MISSING__").astype(str)
    expected = max(0.0, float(record.bundle["model"].predict(frame)[0]))
    assert result["predicted_units"] == expected
    assert result["prediction_target"] == "target_units_next_7d"


def test_stockout_service_matches_canonical_model_and_threshold():
    registry = FrozenModelRegistry()
    record = registry.get("stockout_classification")
    row = _row("data/processed/stockout/stockout_v1.parquet", record.bundle["features"])
    result = StockoutService(registry).predict([row])[0]
    expected = float(record.bundle["model"].predict_proba(pd.DataFrame([row]))[0, 1])
    assert result["stockout_probability"] == expected
    assert result["decision_threshold"] == 0.7695666515458811


def test_serving_rejects_outcome_fields():
    registry = FrozenModelRegistry()
    record = registry.get("forecasting")
    row = _row("data/processed/forecasting/forecasting_v1.parquet", record.bundle["features"])
    row["observed_units"] = 1
    try:
        ForecastService(registry).predict([row])
    except ValueError as exc:
        assert "Forbidden" in str(exc)
    else:
        raise AssertionError("Outcome field was accepted")


def test_api_contract_metadata_and_prediction_routes():
    client = TestClient(create_app())
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
    assert len(client.get("/api/v1/contracts").json()["items"]) == 11
    assert client.get("/api/v1/capabilities").status_code == 200
    registry = FrozenModelRegistry()
    features = registry.get("forecasting").bundle["features"]
    row = _row("data/processed/forecasting/forecasting_v1.parquet", features)
    response = client.post("/api/v1/predict/forecast", json={"rows": [row]})
    assert response.status_code == 200
    assert response.json()["items"][0]["prediction_horizon"] == "(t,t+7d]"


def test_missing_artifacts_make_service_not_ready(tmp_path):
    client = TestClient(create_app(artifact_root=tmp_path))
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 503
