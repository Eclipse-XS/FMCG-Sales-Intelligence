from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..common.paths import project_path, sha256_file


EXPERIMENTS = {
    "forecasting": "fmcg-sales-intelligence/forecasting",
    "stockout_classification": "fmcg-sales-intelligence/stockout-classification",
    "stockout_survival": "fmcg-sales-intelligence/stockout-survival",
    "segmentation": "fmcg-sales-intelligence/segmentation",
    "anomaly": "fmcg-sales-intelligence/anomaly",
    "basket": "fmcg-sales-intelligence/basket",
    "promotion": "fmcg-sales-intelligence/promotion",
}
REGISTERED_MODELS = {
    "forecasting": "fsi.forecasting",
    "stockout_classification": "fsi.stockout_classification",
}


def _numeric_metrics(value: Any, prefix: str = "") -> dict[str, float]:
    result: dict[str, float] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            result.update(_numeric_metrics(child, f"{prefix}.{key}" if prefix else key))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        result[prefix[:250]] = float(value)
    return result


class CanonicalMLflowImporter:
    """Imports persisted evidence only. This module contains no training calls."""

    def __init__(self, tracking_uri: str, artifact_root: str | Path | None = None):
        import mlflow

        self.mlflow = mlflow
        self.mlflow.set_tracking_uri(tracking_uri)
        self.client = mlflow.MlflowClient()
        self.root = Path(artifact_root) if artifact_root else project_path("artifacts", "canonical")

    def sync(self, task: str) -> dict[str, Any]:
        if task not in EXPERIMENTS:
            raise KeyError(task)
        directory = self.root / f"{task}_v1"
        manifest_path, metrics_path = directory / "manifest.json", directory / "metrics.json"
        if not manifest_path.exists() or not metrics_path.exists():
            raise FileNotFoundError(f"Canonical evidence missing for {task}")
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        model_path = directory / "models" / "final_model.joblib"
        if task == "anomaly":
            model_path = directory / "models" / "isolation_forest.joblib"
        identity_source = model_path if model_path.exists() else manifest_path
        identity = f"{task}:v1:{sha256_file(identity_source)}"
        experiment = self.mlflow.set_experiment(EXPERIMENTS[task])
        existing = self.client.search_runs(
            [experiment.experiment_id], f"tags.canonical_identity = '{identity}'", max_results=1
        )
        if existing:
            if task in REGISTERED_MODELS:
                name = REGISTERED_MODELS[task]
                versions = self.client.search_model_versions(
                    f"name = '{name}'",
                    max_results=100,
                )
                matching = [
                    version
                    for version in versions
                    if version.run_id == existing[0].info.run_id
                    and version.tags.get("canonical_identity") == identity
                ]
                if matching:
                    latest = max(matching, key=lambda value: int(value.version))
                    self.client.set_registered_model_alias(name, "serving-v1", latest.version)
            return {
                "task": task,
                "run_id": existing[0].info.run_id,
                "created": False,
                "canonical_identity": identity,
            }
        tags = {
            "project": "fmcg-sales-intelligence",
            "task": task,
            "core_version": "v1",
            "company_profile": "coca_cola_demo",
            "canonical": "true",
            "training_executed": "false",
            "scientific_status": "FROZEN_V1",
            "canonical_identity": identity,
            "source_artifact": "dvc_canonical",
            "synthetic_data": "true",
        }
        with self.mlflow.start_run(experiment_id=experiment.experiment_id, tags=tags) as run:
            self.mlflow.log_metrics(_numeric_metrics(metrics))
            for filename in (
                "manifest.json",
                "metrics.json",
                "selected_model.json",
                "selected_method.json",
                "resolved_config.yaml",
            ):
                path = directory / filename
                if path.exists():
                    self.mlflow.log_artifact(str(path), artifact_path="canonical_metadata")
            if model_path.exists() and task in REGISTERED_MODELS:
                self.mlflow.log_artifact(str(model_path), artifact_path="model_bundle")
                name = REGISTERED_MODELS[task]
                try:
                    self.client.create_registered_model(name, tags={"scientific_status": "FROZEN_V1"})
                except Exception:
                    pass
                version = self.client.create_model_version(
                    name,
                    f"runs:/{run.info.run_id}/model_bundle",
                    run.info.run_id,
                    tags={"canonical_identity": identity, "serving_approved": "true"},
                )
                self.client.set_registered_model_alias(name, "serving-v1", version.version)
            return {"task": task, "run_id": run.info.run_id, "created": True, "canonical_identity": identity}

    def sync_all(self) -> list[dict[str, Any]]:
        return [self.sync(task) for task in EXPERIMENTS]
