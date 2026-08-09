from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from fastapi.testclient import TestClient

from fmcg_sales_intelligence.product.api.app import create_app


ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_backend_usage_runs_without_training_or_canonical_writes() -> None:
    module = _load("backend_integration_example", ROOT / "examples/backend_integration.py")
    result = module.run_direct_usage()
    assert result["external_data_contract"]["validation"]["status"] == "PASS"
    assert result["forecasting"]["result"]["model_version"] == "forecasting_v1"
    assert result["stockout_classification"]["result"]["model_version"] == "stockout_classification_v1"
    assert result["segmentation_membership"]["result"]["review_required"] is True
    assert "survival_probability_day_7" in result["stockout_survival"]["result"]


def test_rest_client_uses_declared_routes_and_bounded_payloads() -> None:
    module = _load("rest_api_client_example", ROOT / "examples/rest_api_client.py")
    assert module.ApiClient("http://localhost:8000/").base_url == "http://localhost:8000"
    assert set(module.FORECAST_ROW) == {
        "lag_1", "lag_7", "lag_14", "lag_28", "sales_velocity_7d", "rolling_mean_7d",
        "rolling_std_7d", "scheduled_selling_price", "store_id", "sku_id", "region_id",
        "brand_name", "category_name", "store_type", "channel",
    }
    client = TestClient(create_app(artifact_root=ROOT / "artifacts/canonical"))
    assert client.post("/api/v1/predict/forecast", json={"rows": [module.FORECAST_ROW]}).status_code == 200
    assert client.post("/api/v1/predict/stockout", json={"rows": [module.STOCKOUT_ROW]}).status_code == 200
    assert client.post("/api/v1/analytics/segments/assign", json={"rows": [module.SEGMENT_ROW]}).status_code == 200
    assert client.get("/api/v1/analytics/anomalies", params={"offset": 2, "limit": 1}).status_code == 200
    assert client.get("/api/v1/analytics/basket-rules", params={"limit": 2}).status_code == 200
    assert client.get("/api/v1/analytics/promotions", params={"offset": 1, "limit": 1}).status_code == 200


def test_usage_notebook_is_compact_executed_and_contains_no_training_calls() -> None:
    notebook = json.loads((ROOT / "examples/fmcg_module_usage.ipynb").read_text(encoding="utf-8"))
    assert 15 <= len(notebook["cells"]) <= 30
    code = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert code and all(cell["execution_count"] is not None for cell in code)
    source = "\n".join("".join(cell["source"]) for cell in code)
    assert ".fit(" not in source
