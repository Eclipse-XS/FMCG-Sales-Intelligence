from __future__ import annotations

import json
import os
from pathlib import Path

from fmcg_sales_intelligence.engine import DomainPack, DomainRegistry, Engine
from fmcg_sales_intelligence.integrations.mlflow import MLflowRegistry
from fmcg_sales_intelligence.product.api.app import create_app as platform_app


def create_app():
    root = Path(__file__).resolve().parent
    deployment = json.loads((Path(os.getenv("DEMO_STATE", "/state")) / "approved-models.json").read_text())
    domain = DomainPack.from_yaml(root / "domain.yaml")
    registry = MLflowRegistry(os.getenv("MLFLOW_TRACKING_URI", "http://registry:5000"),
                              {uri: domain.signature for uri in deployment["approved"]})
    if deployment["signature"] != json.loads(json.dumps(domain.signature.metadata())):
        raise ValueError("Deployment and domain signatures differ")
    if not all(item["ready"] for item in registry.metadata()):
        raise ValueError("Approved SLA models are not ready")
    domains = DomainRegistry()
    domains.register(domain)
    return platform_app(engine=Engine(registry, domains))
