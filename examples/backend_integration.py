"""Direct Python integration with frozen FMCG Sales Intelligence artifacts."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from fmcg_sales_intelligence.product.adapters import FileAdapter
from fmcg_sales_intelligence.product.analytics import AnalyticsReadService
from fmcg_sales_intelligence.product.capabilities import evaluate_capabilities
from fmcg_sales_intelligence.product.contracts import load_registry
from fmcg_sales_intelligence.product.domains import DomainPackRegistry
from fmcg_sales_intelligence.product.serving import (
    ForecastService,
    FrozenModelRegistry,
    SegmentMembershipService,
    StockoutService,
)
from fmcg_sales_intelligence.science.survival import predict_bundle


ROOT = Path(__file__).resolve().parents[1]


def _plain(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def task_feature_row(dataset: Path, features: list[str], *, latest_snapshot: bool = False) -> dict[str, Any]:
    """Read one complete feature row from an already-built task dataset."""
    frame = pd.read_parquet(dataset)
    if latest_snapshot:
        frame = frame[frame["snapshot_date"] == frame["snapshot_date"].max()]
    complete = frame.dropna(subset=features)
    if complete.empty:
        raise ValueError(f"No complete feature row in {dataset}")
    return {name: _plain(complete.iloc[0][name]) for name in features}


def validate_external_sales_sample() -> dict[str, Any]:
    """Normalize a company-shaped CSV through a domain mapping and validate its contract."""
    external = pd.DataFrame(
        [{"day": "2026-09-01", "branch_code": 101, "item_code": 501, "quantity": 12.0}]
    )
    mapping = ROOT / "config/domains/generic_demo/mappings/fixture.yaml"
    with tempfile.TemporaryDirectory(prefix="fsi-example-") as directory:
        source = Path(directory) / "company_sales.csv"
        external.to_csv(source, index=False)
        normalized = FileAdapter(mapping).normalize("sales_daily", source)
    validation = load_registry().validate("sales_daily", normalized)
    return {"normalized_rows": normalized.to_dict(orient="records"), "validation": validation.as_dict()}


def run_direct_usage() -> dict[str, Any]:
    """Exercise only supported frozen inference and read-only analytical interfaces."""
    artifact_root = ROOT / "artifacts/canonical"
    model_registry = FrozenModelRegistry(artifact_root)

    forecast_record = model_registry.get("forecasting")
    forecast_row = task_feature_row(
        ROOT / "data/processed/forecasting/forecasting_v1.parquet",
        forecast_record.bundle["features"],
    )
    forecast = ForecastService(model_registry).predict([forecast_row])[0]

    stockout_record = model_registry.get("stockout_classification")
    stockout_row = task_feature_row(
        ROOT / "data/processed/stockout/stockout_v1.parquet",
        stockout_record.bundle["features"],
    )
    stockout = StockoutService(model_registry).predict([stockout_row])[0]

    segment_service = SegmentMembershipService(artifact_root)
    segment_row = task_feature_row(
        ROOT / "data/processed/segmentation/segmentation_v1.parquet",
        segment_service.features,
        latest_snapshot=True,
    )
    segment_row = {"store_id": 10, **segment_row}
    segment = segment_service.assign([segment_row])[0]

    survival_bundle = joblib.load(
        artifact_root / "stockout_survival_v1/models/final_model.joblib"
    )
    survival_row = task_feature_row(
        ROOT / "data/processed/stockout/stockout_v1.parquet", survival_bundle["features"]
    )
    survival = predict_bundle(survival_bundle, pd.DataFrame([survival_row])).iloc[0].to_dict()
    survival = {key: _plain(value) for key, value in survival.items()}

    analytics = AnalyticsReadService()
    frozen_outputs = {
        name: analytics.read(name, limit=2)
        for name in ("anomalies", "basket-rules", "promotions", "segments")
    }

    profile = DomainPackRegistry().get("generic_demo")
    return {
        "external_data_contract": validate_external_sales_sample(),
        "domain_capabilities": evaluate_capabilities(profile["contracts"]),
        "forecasting": {"input": forecast_row, "result": forecast},
        "stockout_classification": {"input": stockout_row, "result": stockout},
        "segmentation_membership": {"input": segment_row, "result": segment},
        "stockout_survival": {"input": survival_row, "result": survival},
        "offline_frozen_outputs": frozen_outputs,
    }


def main() -> None:
    print(json.dumps(run_direct_usage(), indent=2, default=str))


if __name__ == "__main__":
    main()
