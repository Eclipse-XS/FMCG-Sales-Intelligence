from __future__ import annotations

import ast
from pathlib import Path

from fastapi.testclient import TestClient

from fmcg_sales_intelligence.product.api.app import create_app


def test_airflow_dag_has_no_absolute_project_path():
    source = Path("platform/airflow/dags/fmcg_platform.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert "/opt/airflow/project" not in source
    assert "FSI_PROJECT_ROOT" in source


def test_analytics_region_filter_reaches_query_layer():
    client = TestClient(create_app())
    metadata = client.get("/api/v1/analytics/filters").json()
    region = metadata["regions"][0]
    response = client.get("/api/v1/bi/summary", params={"regions": region})
    assert response.status_code == 200
    assert response.json()["active_stores"] > 0


def test_cors_is_not_wildcard_and_errors_do_not_expose_tracebacks():
    client = TestClient(create_app())
    preflight = client.options(
        "/api/v1/bi/summary",
        headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "GET"},
    )
    assert preflight.headers.get("access-control-allow-origin") != "*"
    invalid = client.get("/api/v1/bi/summary?regions=not-an-integer")
    assert invalid.status_code == 422
    assert "traceback" not in invalid.text.lower()
