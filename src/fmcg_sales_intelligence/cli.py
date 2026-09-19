from __future__ import annotations

import argparse
import json

import uvicorn

from .product.api.settings import Settings
from .product.capabilities import evaluate_capabilities
from .product.contracts import load_registry
from .product.domains import DomainPackRegistry


def main() -> None:
    parser = argparse.ArgumentParser(prog="fsi", description="FMCG Sales Intelligence product CLI")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("contracts-list")
    show = commands.add_parser("contracts-show")
    show.add_argument("contract_id")
    commands.add_parser("company-list")
    validate = commands.add_parser("company-validate")
    validate.add_argument("--profile", required=True)
    capability = commands.add_parser("capabilities")
    capability.add_argument("--profile", required=True)
    serve = commands.add_parser("serve")
    serve.add_argument("--host")
    serve.add_argument("--port", type=int)
    sync = commands.add_parser("mlflow-sync-canonical")
    sync.add_argument(
        "--task",
        choices=[
            "all",
            "forecasting",
            "stockout_classification",
            "stockout_survival",
            "segmentation",
            "anomaly",
            "basket",
            "promotion",
        ],
        default="all",
    )
    args = parser.parse_args()
    registry, packs = load_registry(), DomainPackRegistry()
    if args.command == "contracts-list":
        output = registry.list()
    elif args.command == "contracts-show":
        output = registry.get(args.contract_id)
    elif args.command == "company-list":
        output = packs.list()
    elif args.command == "company-validate":
        profile = packs.get(args.profile)
        known = {c["contract_id"] for c in registry.list()}
        missing = sorted(set(profile["contracts"]) - known)
        output = {
            "profile": args.profile,
            "status": "PASS" if not missing else "FAIL",
            "unknown_contracts": missing,
        }
    elif args.command == "capabilities":
        profile = packs.get(args.profile)
        output = evaluate_capabilities(profile["contracts"])
    elif args.command == "serve":
        settings = Settings()
        uvicorn.run(
            "fmcg_sales_intelligence.product.api.app:app",
            host=args.host or settings.api_host,
            port=args.port or settings.api_port,
        )
        return
    else:
        from .tracking import CanonicalMLflowImporter

        settings = Settings()
        importer = CanonicalMLflowImporter(settings.mlflow_tracking_uri)
        output = importer.sync_all() if args.task == "all" else importer.sync(args.task)
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
