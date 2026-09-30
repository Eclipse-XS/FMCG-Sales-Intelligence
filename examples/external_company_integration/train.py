from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from pathlib import Path

import mlflow
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from fmcg_sales_intelligence.engine import DomainPack
from fmcg_sales_intelligence.integrations.mlflow import MLflowRegistry, register_sklearn
from servicedesk.features import REFERENCE_TIME, extract_features

from generate import SEED, generate

ROOT = Path(__file__).resolve().parent
MODEL = "servicedesk-sla"


def training_data(database, pack):
    with sqlite3.connect(database) as conn:
        conn.row_factory = sqlite3.Row
        tickets = [dict(row) for row in conn.execute("SELECT * FROM tickets ORDER BY ticket_id")]
        labels = [row[0] for row in conn.execute("SELECT sla_breached FROM outcomes ORDER BY ticket_id")]
    external = pd.DataFrame([extract_features(ticket, REFERENCE_TIME) for ticket in tickets])
    return pack.normalize(external), labels


def make_pipeline(regularization):
    return Pipeline([
        ("preprocess", ColumnTransformer([
            ("numeric", StandardScaler(), ["ticket_age_hours", "agent_workload", "sla_target_hours"]),
            ("categorical", OneHotEncoder(handle_unknown="error"), ["priority", "customer_tier", "ticket_status"])])),
        ("classifier", LogisticRegression(C=regularization, random_state=SEED, max_iter=1000))])


def initialize(state: Path, tracking_uri: str):
    state.mkdir(parents=True, exist_ok=True)
    database = Path(os.getenv("TICKET_DATABASE", str(state / "tickets.sqlite")))
    generate(database)
    pack = DomainPack.from_yaml(ROOT / "domain.yaml")
    fingerprint = hashlib.sha256(b"".join((ROOT / p).read_bytes() for p in (
        "generate.py", "train.py", "domain.yaml", "backend/src/servicedesk/features.py"))).hexdigest()
    deployment = state / "approved-models.json"
    if deployment.exists():
        metadata = json.loads(deployment.read_text())
        if metadata["training_fingerprint"] != fingerprint:
            raise ValueError("Demo training inputs changed. Reset this demo's volume before rebuilding.")
        registry = MLflowRegistry(tracking_uri, {uri: pack.signature for uri in metadata["approved"]})
        if not all(model["ready"] for model in registry.metadata()):
            raise ValueError("Existing approved model versions are unavailable; reset the demo volume")
        return metadata
    frame, target = training_data(database, pack)
    approved, predictions = [], {}
    for regularization in (0.3, 1.0):
        pipeline = make_pipeline(regularization)
        pipeline.fit(frame, target)
        uri = register_sklearn(tracking_uri, MODEL, pipeline, pack.signature, frame.head(6), task="classification")
        version = mlflow.MlflowClient(tracking_uri=tracking_uri).get_model_version(MODEL, uri.split("/")[-1])
        client = mlflow.MlflowClient(tracking_uri=tracking_uri)
        client.set_model_version_tag(MODEL, version.version, "training_fingerprint", fingerprint)
        client.set_model_version_tag(MODEL, version.version, "data_kind", "deterministic-synthetic")
        client.set_model_version_tag(MODEL, version.version, "seed", str(SEED))
        approved.append(uri)
        predictions[uri] = pipeline.predict_proba(frame.head(6)).tolist()
    if [uri.split("/")[-1] for uri in approved] != ["1", "2"]:
        raise ValueError("Expected a fresh demo registry with versions 1 and 2. Reset the dedicated demo volume.")
    metadata = {"model": MODEL, "approved": approved, "signature": pack.signature.metadata(),
                "reference_time": REFERENCE_TIME, "seed": SEED, "training_rows": len(frame),
                "training_fingerprint": fingerprint, "python_reference_probabilities": predictions,
                "limitation": "Synthetic demonstration; no claim of real-world predictive accuracy"}
    temporary = state / "approved-models.tmp"
    temporary.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    temporary.replace(deployment)
    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, default=Path(os.getenv("DEMO_STATE", "/state")))
    parser.add_argument("--tracking-uri", default=os.getenv("MLFLOW_TRACKING_URI", "http://registry:5000"))
    args = parser.parse_args()
    result = initialize(args.state, args.tracking_uri)
    print(json.dumps({"approved": result["approved"], "rows": result["training_rows"], "seed": result["seed"]}))


if __name__ == "__main__":
    main()
