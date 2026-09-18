from fmcg_sales_intelligence.analytics import AnalyticsReadService, BusinessIntelligenceService


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
