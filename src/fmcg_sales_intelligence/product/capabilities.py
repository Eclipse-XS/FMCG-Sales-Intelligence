from __future__ import annotations

from typing import Any


CAPABILITIES = {
    "forecasting": {
        "required": ["sales_daily", "sku_master", "locations"],
        "optional": ["prices", "promotions"],
    },
    "stockout_classification": {
        "required": ["inventory_snapshots", "deliveries", "sku_master"],
        "optional": ["sales_daily"],
    },
    "stockout_survival": {
        "required": ["inventory_snapshots", "deliveries", "sku_master"],
        "optional": ["sales_daily"],
    },
    "segmentation": {"required": ["sales_daily", "locations"], "optional": ["prices", "promotions"]},
    "anomaly": {"required": ["sales_daily"], "optional": ["prices", "promotions"]},
    "basket": {"required": ["orders", "order_items", "sku_master"], "optional": []},
    "promotion": {
        "required": ["sales_daily", "promotions", "promotion_stores", "promotion_skus"],
        "optional": ["prices", "inventory_snapshots"],
    },
    "segment_cluster_membership_assignment": {
        "required": ["sales_daily", "locations"],
        "optional": ["prices", "promotions"],
        "experimental": True,
    },
    "supervised_segment_classification": {
        "required": [],
        "optional": [],
        "scientifically_blocked": True,
    },
}


def evaluate_capabilities(
    contracts: list[str], invalid_contracts: list[str] | None = None
) -> list[dict[str, Any]]:
    supplied, invalid = set(contracts), set(invalid_contracts or [])
    results = []
    for name, rule in CAPABILITIES.items():
        required = set(rule["required"])
        if rule.get("scientifically_blocked"):
            status, missing = "BLOCKED_SCIENTIFICALLY", []
        elif required & invalid:
            status, missing = "INVALID_CONTRACT", sorted(required & invalid)
        elif required <= supplied:
            status = "ACTIVE_EXPERIMENTAL" if rule.get("experimental") else "AVAILABLE"
            missing = []
        else:
            status, missing = "UNAVAILABLE_MISSING_CONTRACT", sorted(required - supplied)
        results.append(
            {
                "capability": name,
                "status": status,
                "required_contracts": sorted(required),
                "optional_contracts": rule["optional"],
                "missing_or_invalid": missing,
            }
        )
    return results
