from fmcg_sales_intelligence.analytics import AnalyticsFilters, AnalyticsReadService, BusinessIntelligenceService
from fastapi.testclient import TestClient
from fmcg_sales_intelligence.api.app import create_app


def test_offline_analytics_preserve_caveats():
    service = AnalyticsReadService()
    assert "unreviewed" in service.read("anomalies", limit=1)["caveat"]
    assert "not causation" in service.read("basket-rules", limit=1)["caveat"]
    assert "not causal" in service.read("promotions", limit=1)["caveat"]
    assert "not a validated taxonomy" in service.read("segments", limit=1)["caveat"]


def test_bi_queries_return_supported_metrics_only():
    service = BusinessIntelligenceService()
    summary = service.summary()
    assert summary["units"] > 0 and summary["revenue"] > 0
    assert "profit" not in summary
    assert len(service.timeseries(5)) == 5


def test_bi_filters_are_applied_and_metadata_is_bounded():
    service = BusinessIntelligenceService()
    metadata = service.filter_metadata()
    region = metadata["regions"][0]
    filtered = service.summary(AnalyticsFilters(regions=[region]))
    assert 0 < filtered["active_stores"] <= service.summary()["active_stores"]
    assert len(metadata["skus"]) <= 500


def test_invalid_filter_range_and_oversized_request_are_rejected():
    client = TestClient(create_app())
    response = client.get("/api/v1/bi/summary?date_from=2024-02-01&date_to=2024-01-01")
    assert response.status_code == 422
    oversized = client.post("/api/v1/data/validate", content=b"x" * 2_000_001)
    assert oversized.status_code == 413


def test_security_headers_and_filter_endpoint():
    client = TestClient(create_app())
    response = client.get("/api/v1/analytics/filters")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "regions" in response.json()
