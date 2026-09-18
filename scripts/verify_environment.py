from __future__ import annotations
import json
import sys
from fmcg_sales_intelligence.contracts import load_registry
from fmcg_sales_intelligence.domain_packs import DomainPackRegistry
from fmcg_sales_intelligence.serving import FrozenModelRegistry


def main() -> int:
    result = {
        "python": sys.version.split()[0],
        "contracts": len(load_registry().list()),
        "domain_packs": [p["profile_id"] for p in DomainPackRegistry().list()],
        "models_ready": FrozenModelRegistry().ready,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["models_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
