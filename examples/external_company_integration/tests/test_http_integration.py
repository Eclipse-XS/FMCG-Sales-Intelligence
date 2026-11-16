from __future__ import annotations

import ast
import json
import shutil
import socket
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx
import mlflow
import numpy as np
import pandas as pd
import pytest

from fmcg_sales_intelligence.engine import DomainPack, DomainRegistry, Engine
from fmcg_sales_intelligence.integrations.mlflow import MLflowRegistry
from servicedesk.features import REFERENCE_TIME, extract_features, get_ticket

from generate import generate
from train import make_pipeline, training_data

ROOT = Path(__file__).resolve().parents[1]


def ticket_features(services, ticket_id=1):
    return extract_features(get_ticket(services["database"], ticket_id), REFERENCE_TIME)


def test_runtime_has_no_platform_imports():
    for path in (ROOT / "backend/src/servicedesk").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert "fmcg_sales_intelligence" not in (node.module or "")
            if isinstance(node, ast.Import):
                assert all("fmcg_sales_intelligence" not in alias.name for alias in node.names)
    dependencies = (ROOT / "backend/pyproject.toml").read_text()
    assert "fmcg" not in dependencies and "mlflow" not in dependencies and "scikit" not in dependencies


@pytest.mark.parametrize("version", ["1", "2"])
def test_real_database_http_and_python_prediction_parity(services, version):
    record = httpx.get(services["backend"] + "/tickets/1", trust_env=False).json()
    assert record == get_ticket(services["database"], 1)
    assert "sla_breached" not in record
    features = extract_features(record, REFERENCE_TIME)
    assert features["hours_open"] > 0
    pack, domains = DomainPack.from_yaml(ROOT / "domain.yaml"), DomainRegistry()
    domains.register(pack)
    uri = f"models:/servicedesk-sla/{version}"
    engine = Engine(MLflowRegistry(services["registry"], {uri: pack.signature}), domains)
    python = engine.infer("servicedesk-sla", [features], version=version, domain="servicedesk")
    response = httpx.get(services["backend"] + "/tickets/1/risk", params={"version": version}, timeout=15, trust_env=False)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["model_version"] == version
    assert body["model_uri"] == uri
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert body["model_run_id"] == python["metadata"]["provenance"]["run_id"]
    assert body["sla_breach_probability"] == pytest.approx(python["probabilities"][0][1], abs=1e-12)
    assert body["reference_time"] == REFERENCE_TIME
    deployment = json.loads((services["state"] / "approved-models.json").read_text())
    canonical = pack.normalize(pd.DataFrame([ticket_features(services, i) for i in range(1, 7)]))
    loaded = engine.registry.resolve("servicedesk-sla", version).runtime.estimator
    np.testing.assert_allclose(loaded.predict_proba(canonical), deployment["python_reference_probabilities"][uri], atol=1e-12)


def test_mapping_exact_names_and_values(services):
    external = ticket_features(services)
    pack = DomainPack.from_yaml(ROOT / "domain.yaml")
    canonical = pack.normalize(pd.DataFrame([external]))
    assert list(canonical.columns) == [feature.name for feature in pack.signature.features]
    assert canonical.iloc[0]["ticket_age_hours"] == external["hours_open"]
    assert canonical.iloc[0]["priority"] == external["urgency"]
    assert canonical.iloc[0]["agent_workload"] == external["assigned_agent_open_tickets"]


@pytest.mark.parametrize("mutation", ["missing", "extra", "category", "type", "null", "outcome"])
def test_engine_rejects_incompatible_external_features(services, mutation):
    features = ticket_features(services)
    if mutation == "missing":
        del features["hours_open"]
    elif mutation == "extra":
        features["unknown"] = 1
    elif mutation == "category":
        features["urgency"] = "not-a-priority"
    elif mutation == "type":
        features["assigned_agent_open_tickets"] = "many"
    elif mutation == "null":
        features["sla_hours"] = None
    else:
        features["sla_breached"] = 1
    response = httpx.post(services["engine"] + "/api/v1/models/servicedesk-sla/inferences", json={
        "rows": [features], "version": "2", "domain": "servicedesk"}, trust_env=False)
    assert response.status_code == 422
    assert "error" in response.json()


def test_unknown_ticket_and_version(services):
    for suffix in ("", "/risk"):
        response = httpx.get(services["backend"] + "/tickets/999999" + suffix, trust_env=False)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "TICKET_NOT_FOUND"
    assert httpx.get(services["backend"] + "/tickets/1/risk?version=99", trust_env=False).status_code == 503
    assert httpx.get(services["backend"] + "/tickets/1/risk?version=latest", trust_env=False).status_code == 422


def test_existing_but_unapproved_registry_version_is_denied(services):
    client = mlflow.MlflowClient(tracking_uri=services["registry"], registry_uri=services["registry"])
    versions = client.search_model_versions("name = 'servicedesk-sla'")
    if not any(v.version == "3" for v in versions):
        version = client.get_model_version("servicedesk-sla", "2")
        client.create_model_version("servicedesk-sla", version.source, version.run_id)
    assert client.get_model_version("servicedesk-sla", "3").status == "READY"
    assert httpx.get(services["engine"] + "/api/v1/models/servicedesk-sla?version=3", trust_env=False).status_code == 404
    response = httpx.get(services["backend"] + "/tickets/1/risk?version=3", trust_env=False)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "MODEL_VERSION_UNAVAILABLE"


def test_changed_database_record_changes_inference(services, variant_backend, tmp_path):
    database = tmp_path / "tickets.sqlite"
    shutil.copyfile(services["database"], database)
    with variant_backend(database=database) as url:
        before = httpx.get(url + "/tickets/1/risk", trust_env=False).json()
        with sqlite3.connect(database) as conn:
            conn.execute("UPDATE tickets SET agent_workload = agent_workload + 30 WHERE ticket_id = 1")
        after = httpx.get(url + "/tickets/1/risk", trust_env=False).json()
        assert before["sla_breach_probability"] != after["sla_breach_probability"]
        features = extract_features(get_ticket(database, 1), REFERENCE_TIME)
        remote = httpx.post(services["engine"] + "/api/v1/models/servicedesk-sla/inferences", json={
            "rows": [features], "version": "2", "domain": "servicedesk"}, trust_env=False).json()
        assert after["sla_breach_probability"] == remote["probabilities"][0][1]
        with sqlite3.connect(database) as conn:
            conn.execute("UPDATE tickets SET priority = 'invalid' WHERE ticket_id = 1")
        assert httpx.get(url + "/tickets/1/risk", trust_env=False).status_code == 422


def test_unavailable_engine(variant_backend):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    with variant_backend(engine=f"http://127.0.0.1:{port}") as url:
        response = httpx.get(url + "/tickets/1/risk", trust_env=False)
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "ENGINE_UNAVAILABLE"
        assert "Traceback" not in response.text and "/state" not in response.text


def test_read_timeout_and_sanitized_upstream_failure(variant_backend):
    class Handler(BaseHTTPRequestHandler):
        slow = True
        def do_POST(self):
            if self.slow:
                time.sleep(0.4)
            self.send_response(500)
            self.end_headers()
            try:
                self.wfile.write(b"secret-internal-error-path")
            except BrokenPipeError:
                pass
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with variant_backend(engine=f"http://127.0.0.1:{server.server_port}", request_timeout=0.1) as url:
            response = httpx.get(url + "/tickets/1/risk", trust_env=False)
            assert response.status_code == 504
            Handler.slow = False
            response = httpx.get(url + "/tickets/1/risk", trust_env=False)
            assert response.status_code == 502
            assert "secret-internal" not in response.text
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_deterministic_generation_and_future_data_excluded(tmp_path):
    a, b = tmp_path / "a.sqlite", tmp_path / "b.sqlite"
    generate(a)
    generate(b)
    with sqlite3.connect(a) as left, sqlite3.connect(b) as right:
        for table in ("tickets", "outcomes"):
            assert left.execute(f"SELECT * FROM {table} ORDER BY ticket_id").fetchall() == right.execute(f"SELECT * FROM {table} ORDER BY ticket_id").fetchall()
        for record in left.execute("SELECT ticket_id FROM tickets"):
            observed = get_ticket(a, record[0])
            assert extract_features(observed, REFERENCE_TIME)["hours_open"] < observed["sla_hours"]
        ticket = get_ticket(a, 1)
        features = extract_features(ticket, REFERENCE_TIME)
        left.execute("UPDATE outcomes SET sla_breached=1-sla_breached, future_resolution_hours=9999")
        left.commit()
        assert extract_features(get_ticket(a, 1), REFERENCE_TIME) == features
    with pytest.raises(ValueError, match="snapshot"):
        extract_features(ticket, "2026-01-14T12:00:00+00:00")


def test_retraining_reproduces_registered_pipeline(services):
    pack = DomainPack.from_yaml(ROOT / "domain.yaml")
    frame, target = training_data(services["database"], pack)
    pipeline = make_pipeline(0.3).fit(frame, target)
    deployment = json.loads((services["state"] / "approved-models.json").read_text())
    assert set(target) == {0, 1}
    np.testing.assert_allclose(pipeline.predict_proba(frame.head(6)),
                               deployment["python_reference_probabilities"]["models:/servicedesk-sla/1"], atol=1e-12)
