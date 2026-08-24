
import pytest
from fastapi.testclient import TestClient

from fmcg_sales_intelligence.engine import Engine, EngineError, Feature, MemoryRegistry, Model, Signature
from fmcg_sales_intelligence.integrations.demo import build_demo
from fmcg_sales_intelligence.integrations.fmcg import register_frozen_models
from fmcg_sales_intelligence.integrations.mlflow import MLflowRegistry, register_sklearn
from fmcg_sales_intelligence.integrations.trust import load_approved_bundle
from fmcg_sales_intelligence.product.api.app import create_app
from fmcg_sales_intelligence.product.api.settings import Settings
from fmcg_sales_intelligence.product.serving import ForecastService, FrozenModelRegistry, StockoutService


def test_rest_python_parity_and_metadata(tmp_path):
    engine, *_ = build_demo()
    client = TestClient(create_app(engine=engine, artifact_root=tmp_path))
    row = {"months": "12", "fee": "75", "plan": "monthly"}
    sdk = engine.infer("customer-churn", [row], version="1", domain="customer-retention")
    response = client.post("/api/v1/models/customer-churn/inferences", json={"rows": [row], "version": "1",
                           "domain": "customer-retention"}, headers={"X-Request-ID": "integration-test"})
    assert response.status_code == 200
    result = response.json()
    assert result["predictions"] == sdk["predictions"]
    assert result["probabilities"] == sdk["probabilities"]
    assert result["metadata"]["version"] == "1"
    assert result["metadata"]["request_id"] == "integration-test"
    assert client.get("/api/v1/models/customer-churn/schema").json()["forbidden"] == ["churned"]
    assert len(client.get("/api/v1/domains").json()["items"]) == 2
    assert client.get("/api/v1/runtime/ready").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 503  # legacy artifacts independent of engine readiness
    assert client.post("/api/v1/models/customer-churn/validate", json={"rows": [row], "domain": "customer-retention"}).json()["valid"]


def test_api_errors_and_resource_limits(tmp_path):
    engine, *_ = build_demo()
    engine.registry.register(Model("offline", "1", "regression", Signature((Feature("x", "number"),)), None))
    client = TestClient(create_app(engine=engine, artifact_root=tmp_path, settings=Settings(max_request_bytes=400)))
    for name, rows, status in [("unknown", [{"x": 1}], 404), ("offline", [{"x": 1}], 503),
                                ("customer-churn", [{"x": 1}], 422)]:
        response = client.post(f"/api/v1/models/{name}/inferences", json={"rows": rows})
        assert response.status_code == status
        assert "request_id" in response.json()["error"]
        assert "Traceback" not in response.text
    assert client.post("/api/v1/models/offline/inferences", json={"rows": []}).status_code == 422
    assert client.post("/api/v1/models/offline/inferences", json={"rows": [{"x": 1}], "file": "bad.pkl"}).status_code == 422
    # No Content-Length header: actual streamed bytes still bounded.
    assert client.post("/api/v1/models/offline/inferences", content=iter([b" " * 250, b" " * 250])).status_code == 413
    assert client.post("/api/v1/predict/forecast", json={"rows": [{"x": 1}]}).status_code == 503
    assert client.post("/api/v1/business/forecast", json={"store_id": 1, "sku_id": 1}).status_code == 503


def test_frozen_bridge_preserves_predictions(canonical_fixture):
    frozen, deployed = FrozenModelRegistry(canonical_fixture), MemoryRegistry()
    register_frozen_models(deployed, frozen)
    engine = Engine(deployed)
    row = {"signal": 2.}
    assert engine.infer("forecasting", [row])["predictions"] == [ForecastService(frozen).predict([row])[0]["predicted_units"]]
    assert engine.infer("stockout_classification", [row])["predictions"] == [StockoutService(frozen).predict([row])[0]["stockout_probability"]]
    client = TestClient(create_app(artifact_root=canonical_fixture))
    assert client.post("/api/v1/models/forecasting/inferences", json={"rows": [row]}).status_code == 200
    assert client.get("/ready").status_code == 200
    (canonical_fixture / "trusted-artifacts.json").write_text("{}")
    assert not FrozenModelRegistry(canonical_fixture).ready


def test_artifact_rejection_before_deserialization(canonical_fixture, monkeypatch):
    import joblib
    artifact = canonical_fixture / "forecasting_v1/models/final_model.joblib"
    called = []
    monkeypatch.setattr(joblib, "load", lambda path: called.append(path))
    artifact.write_bytes(b"not-approved")
    with pytest.raises(ValueError, match="hash is not approved"):
        load_approved_bundle(artifact, canonical_fixture / "trusted-artifacts.json")
    assert not called


def test_mlflow_pipeline_registration_versions_and_loading(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine, pipeline, signature, frame = build_demo()
    tracking = "sqlite:///registry.db"
    uri1 = register_sklearn(tracking, "external-model", pipeline, signature, frame.head(3), task="classification")
    uri2 = register_sklearn(tracking, "external-model", pipeline, signature, frame.head(3), task="classification")
    assert uri1 == "models:/external-model/1"
    assert uri2 == "models:/external-model/2"
    registry = MLflowRegistry(tracking, {uri1: signature, uri2: signature})
    with pytest.raises(EngineError) as exc:
        registry.resolve("external-model")
    assert exc.value.code == "VERSION_REQUIRED"
    restored = Engine(registry).infer("external-model", frame.head(3), version="1")
    assert restored["predictions"] == engine.infer("customer-churn", frame.head(3))["predictions"]
    assert restored["metadata"]["provenance"]["uri"] == uri1
    with pytest.raises(EngineError):
        registry.resolve("external-model", "3")
    with pytest.raises(ValueError):
        MLflowRegistry(tracking, {"models:/external-model/latest": signature})
    wrong = Signature(tuple(reversed(signature.features)))
    assert not MLflowRegistry(tracking, {uri1: wrong}).resolve("external-model", "1").metadata()["ready"]
    client = TestClient(create_app(engine=Engine(registry), artifact_root=tmp_path))
    response = client.post("/api/v1/models/external-model/inferences", json={"rows": frame.head(3).to_dict(orient="records"), "version": "2"})
    assert response.status_code == 200
    assert response.json()["predictions"] == restored["predictions"]
