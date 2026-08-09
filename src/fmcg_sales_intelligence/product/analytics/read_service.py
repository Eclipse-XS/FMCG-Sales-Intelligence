from __future__ import annotations

from typing import Any

import pandas as pd

from ...common.paths import project_path


class AnalyticsReadService:
    SOURCES = {
        "segments": (
            "artifacts/canonical/segmentation_v1/predictions_or_labels/store_segments.parquet",
            "exploratory segments; not a validated taxonomy",
        ),
        "segment-profiles": (
            "artifacts/canonical/segmentation_v1/diagnostics/cluster_profiles.csv",
            "cluster center standardized features",
        ),
        "anomalies": (
            "artifacts/canonical/anomaly_v1/predictions_or_scores/review_candidates.csv",
            "unreviewed anomaly candidates",
        ),
        "basket-rules": (
            "artifacts/canonical/basket_v1/outputs/association_rules.parquet",
            "association; not causation or recommendation",
        ),
        "promotions": (
            "artifacts/canonical/promotion_v1/outputs/promotion_summary.parquet",
            "descriptive comparison; not causal effect",
        ),
    }

    def read(self, name: str, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        if name not in self.SOURCES:
            raise KeyError(name)
        relative, caveat = self.SOURCES[name]
        path = project_path(*relative.split("/"))
        if not path.exists():
            return {"name": name, "status": "UNAVAILABLE", "caveat": caveat, "total": 0, "items": []}
        frame = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
        import numpy as np
        page = frame.iloc[offset : offset + min(limit, 500)].copy()
        items = page.to_dict(orient="records")
        for item in items:
            for k, v in item.items():
                if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                    item[k] = None
        return {
            "name": name,
            "status": "AVAILABLE",
            "caveat": caveat,
            "total": len(frame),
            "offset": offset,
            "limit": min(limit, 500),
            "items": items,
        }
