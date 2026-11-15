import pandas as pd
from fmcg_sales_intelligence.engine import Engine, MemoryRegistry
from fmcg_sales_intelligence.integrations.fmcg import register_frozen_models
from fmcg_sales_intelligence.product.serving import FrozenModelRegistry, ForecastService, StockoutService


def test_real_frozen_models_through_engine_are_numerically_identical():
    frozen, registry = FrozenModelRegistry(), MemoryRegistry()
    register_frozen_models(registry, frozen)
    for name, dataset, service, output in [
        ("forecasting", "forecasting", ForecastService, "predicted_units"),
        ("stockout_classification", "stockout", StockoutService, "stockout_probability"),
    ]:
        record = frozen.get(name)
        frame = pd.read_parquet(f"data/processed/{dataset}/{dataset}_v1.parquet")[record.bundle["features"]].dropna().head(8)
        expected = [r[output] for r in service(frozen).predict(frame.to_dict(orient="records"))]
        result = Engine(registry).infer(name, frame, version=record.version)
        assert result["predictions"] == expected
        assert result["metadata"]["provenance"]["sha256"] == record.fingerprint
