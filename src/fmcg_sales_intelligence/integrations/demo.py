from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ..engine import DomainPack, DomainRegistry, Engine, Feature, MemoryRegistry, Model, Predictor, Signature


def build_demo():
    rng = np.random.default_rng(42)
    frame = pd.DataFrame({"tenure_months": rng.integers(1, 72, 160).astype(float),
                          "monthly_charge": rng.uniform(15, 120, 160),
                          "contract": rng.choice(["monthly", "annual"], 160)})
    target = ((frame.tenure_months < 24) & (frame.contract == "monthly") | (frame.monthly_charge > 100)).astype(int)
    signature = Signature((Feature("tenure_months", "number", coerce=True),
                           Feature("monthly_charge", "number", coerce=True),
                           Feature("contract", "string", categories=("monthly", "annual"))), ("churned",))
    preprocessing = ColumnTransformer([
        ("numeric", StandardScaler(), ["tenure_months", "monthly_charge"]),
        ("category", OneHotEncoder(handle_unknown="error"), ["contract"])])
    pipeline = Pipeline([("preprocessing", preprocessing), ("model", LogisticRegression(random_state=42))])
    pipeline.fit(signature.validate(frame), target)
    registry, domains = MemoryRegistry(), DomainRegistry()
    registry.register(Model("customer-churn", "1", "classification", signature,
                            Predictor(pipeline, probabilities=True), ("predictions", "probabilities", "classes"),
                            {"dataset": "deterministic synthetic", "seed": 42}))
    domains.register(DomainPack("customer-retention", "1", signature,
                                {"months": "tenure_months", "fee": "monthly_charge", "plan": "contract"}))

    # Deliberately small reference regression; canonical scientific results remain separate.
    sales = pd.DataFrame({"lag_units": rng.uniform(0, 100, 160), "price": rng.uniform(1, 20, 160)})
    sales_signature = Signature((Feature("lag_units", "number"), Feature("price", "number")), ("future_units",))
    regressor = Pipeline([("scale", StandardScaler()), ("model", Ridge())])
    regressor.fit(sales, np.maximum(0, 1.2 * sales.lag_units - sales.price))
    registry.register(Model("demand-demo", "1", "forecasting", sales_signature,
                            Predictor(regressor, clip_lower=0), provenance={"dataset": "synthetic smoke fixture"}))
    domains.register(DomainPack("fmcg-demo", "1", sales_signature, {"previous_units": "lag_units", "unit_price": "price"}))
    return Engine(registry, domains), pipeline, signature, frame


def create_demo_app():
    from ..product.api.app import create_app
    engine, _, _, _ = build_demo()
    return create_app(engine=engine)


def main():
    parser = argparse.ArgumentParser(description="Deterministic tabular engine demo, independent of private artifacts")
    parser.add_argument("--output", type=Path, default=Path(".demo"))
    parser.add_argument("--mlflow-uri")
    args = parser.parse_args()
    engine, pipeline, signature, frame = build_demo()
    args.output.mkdir(parents=True, exist_ok=True)
    external = frame.head(4).rename(columns={"tenure_months": "months", "monthly_charge": "fee", "contract": "plan"})
    source = args.output / "customers.csv"
    external.to_csv(source, index=False)
    external.to_parquet(args.output / "customers.parquet", index=False)
    python = engine.infer("customer-churn", source, domain="customer-retention")
    # Real HTTP protocol is separately exercised by integration tests and uvicorn smoke.
    from fastapi.testclient import TestClient
    from ..product.api.app import create_app
    client = TestClient(create_app(engine=engine))
    response = client.post("/api/v1/models/customer-churn/inferences", json={
        "rows": external.to_dict(orient="records"), "domain": "customer-retention", "version": "1"})
    response.raise_for_status()
    assert python["predictions"] == response.json()["predictions"]
    evidence = {"python": python, "rest": response.json(),
                "demand": engine.infer("demand-demo", [{"previous_units": 30., "unit_price": 4.}], domain="fmcg-demo")}
    if args.mlflow_uri:
        from .mlflow import MLflowRegistry, register_sklearn
        uri = register_sklearn(args.mlflow_uri, "customer-churn", pipeline, signature, frame.head(4), task="classification")
        deployed = Engine(MLflowRegistry(args.mlflow_uri, {uri: signature}))
        evidence["mlflow"] = deployed.infer("customer-churn", frame.head(4), version=uri.split("/")[-1])
    (args.output / "evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
