from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from ...common.paths import project_path, sha256_file


class SegmentMembershipService:
    """Assign stores with the frozen exploratory KMeans state; never fit here."""

    VERSION = "segmentation_v1"
    METHOD = "frozen_kmeans_predict"

    def __init__(self, artifact_root: str | Path | None = None):
        root = Path(artifact_root) if artifact_root else project_path("artifacts", "canonical")
        self.artifact = root / self.VERSION / "models" / "final_model.joblib"
        if not self.artifact.is_file():
            raise FileNotFoundError("Frozen segmentation artifact is unavailable")
        state = joblib.load(self.artifact)
        required = {"preprocessor", "model", "features", "canonical_mapping", "segment_names", "version"}
        if not required.issubset(state) or state.get("algorithm") != "kmeans":
            raise ValueError("Frozen segmentation artifact does not support native membership assignment")
        self.preprocessor = state["preprocessor"]
        self.model = state["model"]
        self.features = list(state["features"])
        self.mapping = {int(k): int(v) for k, v in state["canonical_mapping"].items()}
        self.names = {int(k): str(v) for k, v in state["segment_names"].items()}
        self.version = str(state["version"])
        self.fingerprint = sha256_file(self.artifact)

    def assign(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        allowed = {"store_id", *self.features}
        normalized: list[dict[str, Any]] = []
        for row in rows:
            missing = [feature for feature in self.features if feature not in row]
            unknown = sorted(set(row) - allowed)
            if missing:
                raise ValueError(f"Missing required segmentation features: {missing}")
            if unknown:
                raise ValueError(f"Unsupported segmentation fields: {unknown}")
            values: dict[str, float] = {}
            for feature in self.features:
                value = row[feature]
                try:
                    numeric = float(value)
                except (TypeError, ValueError):
                    numeric = float("nan")
                if isinstance(value, bool) or not math.isfinite(numeric):
                    raise ValueError(f"Feature {feature} must be a finite number")
                values[feature] = numeric
            normalized.append({"store_id": row.get("store_id"), **values})

        frame = pd.DataFrame(normalized)
        transformed = self.preprocessor.transform(frame[self.features])
        native = self.model.predict(transformed)
        distances = self.model.transform(transformed)
        result = []
        for index, native_cluster in enumerate(native):
            cluster_id = self.mapping[int(native_cluster)]
            result.append(
                {
                    "store_id": normalized[index]["store_id"],
                    "cluster_id": cluster_id,
                    "profile_label": self.names[cluster_id],
                    "centroid_distance": float(distances[index, int(native_cluster)]),
                    "segmentation_model_version": self.version,
                    "feature_contract_version": "segmentation_features_v1",
                    "artifact_fingerprint": self.fingerprint,
                    "assignment_method": self.METHOD,
                    "scientific_status": "exploratory",
                    "taxonomy_stability": "limited",
                    "review_required": True,
                    "label_semantics": "PSEUDO_LABEL_NOT_GROUND_TRUTH",
                }
            )
        return result
