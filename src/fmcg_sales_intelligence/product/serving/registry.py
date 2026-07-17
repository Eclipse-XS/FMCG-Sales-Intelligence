from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

from ...common.paths import project_path, relative_path, sha256_file


@dataclass
class ModelRecord:
    name: str
    version: str
    task: str
    artifact: Path
    manifest: dict[str, Any]
    bundle: dict[str, Any] | None
    fingerprint: str | None
    error: str | None = None

    @property
    def ready(self) -> bool:
        return self.bundle is not None and self.error is None

    def public_metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "task": self.task,
            "ready": self.ready,
            "prediction_horizon": self.manifest.get("prediction_horizon", "(t,t+7d]"),
            "artifact_fingerprint": self.fingerprint,
            "feature_contract_version": "v1",
            "target": self.manifest.get("target"),
            "limitation": "Frozen synthetic-data V1 model; local demonstration only.",
        }


class FrozenModelRegistry:
    SPECS = {
        "forecasting": ("forecasting_v1", "models/final_model.joblib"),
        "stockout_classification": ("stockout_classification_v1", "models/final_model.joblib"),
    }

    def __init__(self, artifact_root: str | Path | None = None):
        self.artifact_root = Path(artifact_root) if artifact_root else project_path("artifacts", "canonical")
        self.records = {name: self._load(name, version, rel) for name, (version, rel) in self.SPECS.items()}

    def _load(self, name: str, version: str, rel: str) -> ModelRecord:
        root = self.artifact_root / version
        artifact, manifest_path = root / rel, root / "manifest.json"
        manifest: dict[str, Any] = {}
        try:
            if not artifact.is_file() or not manifest_path.is_file():
                raise FileNotFoundError(f"Required canonical files are unavailable for {version}")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            bundle = joblib.load(artifact)
            if list(bundle.get("features", [])) != list(manifest.get("features", [])):
                raise ValueError("Model bundle and manifest feature contracts differ")
            if bundle.get("target") != manifest.get("target"):
                raise ValueError("Model bundle and manifest target differ")
            return ModelRecord(
                name, version, manifest.get("task", name), artifact, manifest, bundle, sha256_file(artifact)
            )
        except Exception as exc:
            return ModelRecord(
                name, version, name, artifact, manifest, None, None, f"{type(exc).__name__}: {exc}"
            )

    @property
    def ready(self) -> bool:
        return all(record.ready for record in self.records.values())

    def get(self, name: str) -> ModelRecord:
        if name not in self.records:
            raise KeyError(name)
        return self.records[name]

    def metadata(self) -> list[dict[str, Any]]:
        return [record.public_metadata() for record in self.records.values()]

    def serialization_catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "task": r.task,
                "serializer": "joblib",
                "artifact": relative_path(r.artifact),
                "preprocessor_included": r.name == "stockout_classification",
                "model_included": r.ready,
                "feature_contract_included": bool(r.manifest.get("features")),
                "load_test": "PASS" if r.ready else "FAIL",
                "serving_approved": r.ready,
            }
            for r in self.records.values()
        ]
