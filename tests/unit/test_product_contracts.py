from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd

from fmcg_sales_intelligence.product.capabilities import evaluate_capabilities
from fmcg_sales_intelligence.product.contracts import load_registry
from fmcg_sales_intelligence.product.domains import DomainPackRegistry


def test_contract_registry_is_versioned_and_complete():
    registry = load_registry()
    contracts = registry.list()
    assert registry.payload["registry_version"] == "v1"
    assert len(contracts) == 11
    assert all(item["grain"] and item["business_key"] and item["consumers"] for item in contracts)
    assert len({(x["contract_id"], x["contract_version"]) for x in contracts}) == len(contracts)


def test_contract_validation_detects_duplicates_and_required_nulls():
    frame = pd.DataFrame(
        [
            {"observation_date": "2024-01-01", "store_id": 1, "sku_id": 2, "observed_units": 3},
            {"observation_date": "2024-01-01", "store_id": 1, "sku_id": 2, "observed_units": None},
        ]
    )
    report = load_registry().validate("sales_daily", frame)
    assert report.status == "FAIL"
    assert report.duplicate_key_count == 1
    assert report.null_failures == {"observed_units": 1}


def test_domain_packs_and_capability_semantics():
    packs = DomainPackRegistry()
    coca, generic = packs.get("coca_cola_demo"), packs.get("generic_demo")
    assert coca["display_name"] != generic["display_name"]
    generic_caps = {x["capability"]: x["status"] for x in evaluate_capabilities(generic["contracts"])}
    assert generic_caps["forecasting"] == "AVAILABLE"
    assert generic_caps["basket"] == "UNAVAILABLE_MISSING_CONTRACT"
    assert generic_caps["segment_cluster_membership_assignment"] == "ACTIVE_EXPERIMENTAL"
    assert generic_caps["supervised_segment_classification"] == "BLOCKED_SCIENTIFICALLY"


def test_generic_package_does_not_import_coca_cola_pack():
    root = Path("src/fmcg_sales_intelligence")
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        names += [
            alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names
        ]
        assert all("coca_cola_demo" not in name for name in names)
