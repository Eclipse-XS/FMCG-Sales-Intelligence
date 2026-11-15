from pathlib import Path

import pandas as pd
import pytest

from fmcg_sales_intelligence.engine import DomainPack, Engine, EngineError, Feature, MemoryRegistry, Model, Predictor, Signature
from fmcg_sales_intelligence.integrations.demo import build_demo


@pytest.mark.parametrize("row,code", [
    ({"tenure_months": 2, "contract": "annual"}, "MISSING_FEATURE"),
    ({"tenure_months": 2, "monthly_charge": None, "contract": "annual"}, "NULL_FEATURE"),
    ({"tenure_months": True, "monthly_charge": 3, "contract": "annual"}, "INVALID_FEATURE"),
    ({"tenure_months": 2, "monthly_charge": "broken", "contract": "annual"}, "INVALID_FEATURE"),
    ({"tenure_months": 2, "monthly_charge": float("inf"), "contract": "annual"}, "INVALID_FEATURE"),
    ({"tenure_months": 2, "monthly_charge": 3, "contract": "unknown"}, "INVALID_FEATURE"),
    ({"tenure_months": 2, "monthly_charge": 3, "contract": "annual", "churned": 1}, "FORBIDDEN_FEATURE"),
    ({"tenure_months": 2, "monthly_charge": 3, "contract": "annual", "extra": 1}, "UNEXPECTED_FEATURE"),
])
def test_input_contract(row, code):
    engine, *_ = build_demo()
    with pytest.raises(EngineError) as exc:
        engine.infer("customer-churn", [row])
    assert exc.value.code == code


def test_sources_and_mapping(tmp_path):
    engine, _, _, data = build_demo()
    external = data.head(4).rename(columns={"tenure_months": "months", "monthly_charge": "fee", "contract": "plan"})
    direct = engine.infer("customer-churn", data.head(4))["predictions"]
    for suffix in ("csv", "parquet"):
        path = tmp_path / f"source.{suffix}"
        if suffix == "csv":
            external.to_csv(path, index=False)
        else:
            external.to_parquet(path, index=False)
        assert engine.infer("customer-churn", path, domain="customer-retention")["predictions"] == direct
    assert engine.infer("customer-churn", external, domain="customer-retention")["predictions"] == direct
    assert list(external.columns) == ["months", "fee", "plan"]


def test_missing_individual_key_even_nullable():
    engine, *_ = build_demo()
    with pytest.raises(EngineError, match="same feature keys"):
        engine.infer("customer-churn", [{"tenure_months": 1}, {"monthly_charge": 3}])


def test_versions_and_registration():
    engine, pipeline, signature, frame = build_demo()
    engine.registry.register(Model("customer-churn", "2", "classification", signature, Predictor(pipeline)))
    with pytest.raises(EngineError) as exc:
        engine.infer("customer-churn", frame.head(1))
    assert exc.value.code == "VERSION_REQUIRED"
    assert engine.infer("customer-churn", frame.head(1), version="1")["metadata"]["version"] == "1"
    with pytest.raises(EngineError) as exc:
        engine.registry.register(engine.registry.resolve("customer-churn", "1"))
    assert exc.value.status == 409
    with pytest.raises(ValueError, match="names/order"):
        Model("bad", "1", "regression", Signature(tuple(reversed(signature.features))), Predictor(pipeline))


def test_task_output_and_failure():
    class BadRuntime:
        def execute(self, frame):
            return {"predictions": [float("nan")]}
    signature = Signature((Feature("x", "number"),))
    registry = MemoryRegistry()
    registry.register(Model("bad", "1", "regression", signature, BadRuntime()))
    registry.register(Model("missing", "1", "scoring", signature, None))
    for name, status in [("bad", 500), ("missing", 503), ("unknown", 404)]:
        with pytest.raises(EngineError) as exc:
            Engine(registry).infer(name, [{"x": 1}])
        assert exc.value.status == status


def test_batch_limits_and_transform_revalidation():
    engine, *_ = build_demo()
    for rows in ([], [{"x": 1}] * 1001):
        with pytest.raises(EngineError) as exc:
            engine.infer("customer-churn", rows)
        assert exc.value.code == "INVALID_BATCH"
    signature = Signature((Feature("lag_units", "number"), Feature("price", "number")))
    engine.domains.register(DomainPack("broken", "1", signature, transform=lambda frame: frame.assign(future_units=10)))
    with pytest.raises(EngineError, match="future"):
        engine.infer("demand-demo", [{"lag_units": 3., "price": 2.}], domain="broken")


def test_types_coercion_and_nullability():
    signature = Signature((Feature("count", "integer", coerce=True), Feature("flag", "boolean"),
                           Feature("time", "datetime", coerce=True), Feature("name", "string", nullable=True)))
    valid = pd.DataFrame([{"count": "2", "flag": True, "time": "2024-01-01", "name": None}])
    assert signature.validate(valid)["count"].iloc[0] == 2
    for column, value in [("count", 2.5), ("flag", "false"), ("time", "yesterday-ish")]:
        with pytest.raises(EngineError):
            signature.validate(valid.assign(**{column: value}))


def test_mapping_collisions_and_forbidden_fields():
    engine, *_ = build_demo()
    with pytest.raises(EngineError):
        engine.infer("customer-churn", [{"months": 2, "fee": 3, "plan": "annual", "churned": 1}],
                     domain="customer-retention")
    signature = Signature((Feature("x", "number"),))
    pack = DomainPack("collision", "1", signature, {"a": "x"})
    with pytest.raises(EngineError):
        pack.normalize(pd.DataFrame([{"a": 1, "x": 2}]))


def test_core_dependency_direction():
    import ast
    root = Path("src/fmcg_sales_intelligence/engine")
    for path in root.glob("*.py"):
        source = path.read_text()
        ast.parse(source)
        assert not any(word in source.lower() for word in ("sku", "warehouse", "stockout", "coca", "replenishment"))
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom):
                assert not any(part in (node.module or "") for part in ("product", "science", "integrations", "fastapi"))
def test_declarative_pack_matches_reviewed_demo():
    from fmcg_sales_intelligence.engine import DomainPack
    engine, _, signature, _ = build_demo()
    pack = DomainPack.from_yaml("config/domains/customer_retention/engine.yaml")
    assert pack.signature == signature
    assert pack.mapping == engine.domains.get("customer-retention").mapping
