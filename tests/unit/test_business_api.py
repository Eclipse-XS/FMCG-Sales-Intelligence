from fastapi.testclient import TestClient

from fmcg_sales_intelligence.product.api.app import app

client = TestClient(app)

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
