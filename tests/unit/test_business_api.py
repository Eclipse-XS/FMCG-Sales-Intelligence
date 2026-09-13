from fastapi.testclient import TestClient

import pytest
from fmcg_sales_intelligence.product.api.app import create_app
from fmcg_sales_intelligence.product.serving.resolver import FeatureResolver

@pytest.fixture(autouse=True)
def isolated_client(canonical_fixture, monkeypatch):
    global client
    def forecast(self, store_id, sku_id):
        return {"signal": 2., "prediction_date": "2024-01-01"} if store_id == sku_id == 1 else None
    def stockout(self, warehouse_id, sku_id):
        return {"signal": 2., "prediction_date": "2024-01-01"} if warehouse_id == sku_id == 1 else None
    def segment(self, store_id):
        return {"store_id": store_id, "revenue_30d": 2., "average_price_30d": 3.,
                "promotion_unit_share_30d": 4., "revenue_volatility_30d": 5.}
    monkeypatch.setattr(FeatureResolver, "resolve_forecast_features", forecast)
    monkeypatch.setattr(FeatureResolver, "resolve_stockout_features", stockout)
    monkeypatch.setattr(FeatureResolver, "resolve_segmentation_features", segment)
    client = TestClient(create_app(artifact_root=canonical_fixture))

def test_business_forecast_success():
    # Use real store and sku that should exist
    response = client.post("/api/v1/business/forecast", json={"store_id": 1, "sku_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert "predicted_units" in item
    assert "as_of_date" in item
    assert item["store_id"] == 1
    assert item["sku_id"] == 1
    assert "prediction_target" in item
    assert "prediction_horizon" in item

def test_business_forecast_not_found():
    # Unknown store
    response = client.post("/api/v1/business/forecast", json={"store_id": 9999, "sku_id": 9999})
    assert response.status_code == 404

def test_business_stockout_success():
    response = client.post("/api/v1/business/stockout", json={"warehouse_id": 1, "sku_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert "stockout_probability" in item
    assert "risk_flag" in item
    assert "as_of_date" in item
    assert item["warehouse_id"] == 1
    assert item["sku_id"] == 1

def test_business_segmentation_success():
    response = client.post("/api/v1/business/segments/assign", json={"store_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert "cluster_id" in item
    assert "profile_label" in item
    assert "scientific_status" in item
    assert item["scientific_status"] == "exploratory"

def test_json_safety_inf_nan():
    # Check that reading anomalies (which has nan/inf in raw) returns 200 OK without pydantic JSON errors
    response = client.get("/api/v1/analytics/anomalies?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_low_level_backward_compatibility():
    # Forecast requires lots of features. We don't have to provide all if it fails gracefully with 422
    response = client.post("/api/v1/predict/forecast", json={"rows": [{"store_id": 1}]})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert "code" in data["error"]
    assert data["error"]["code"] == "INVALID_INPUT"
    assert "Missing required features" in data["error"]["message"]
