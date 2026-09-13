import hashlib
import json

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@pytest.fixture
def canonical_fixture(tmp_path):
    """Tiny local artifacts; never overwrite canonical experiments or their metrics."""
    root = tmp_path / "artifacts"
    x = pd.DataFrame({"signal": [0., 1., 2., 3., 4., 5.]})
    for name, model in [("forecasting", Ridge().fit(x, np.arange(6.))),
                        ("stockout_classification", LogisticRegression().fit(x, [0, 0, 0, 1, 1, 1]))]:
        directory = root / f"{name}_v1"
        (directory / "models").mkdir(parents=True)
        bundle = {"model": model, "features": ["signal"], "categorical": [],
                  "target": "target_units_next_7d" if name == "forecasting" else "stockout_within_7d",
                  "threshold": 0.5, "clip_lower": 0}
        joblib.dump(bundle, directory / "models/final_model.joblib")
        (directory / "manifest.json").write_text(json.dumps({"features": bundle["features"], "target": bundle["target"]}))
    features = ["revenue_30d", "average_price_30d", "promotion_unit_share_30d", "revenue_volatility_30d"]
    segment_x = pd.DataFrame(np.arange(24).reshape(6, 4), columns=features)
    prep = Pipeline([("scale", StandardScaler())]).fit(segment_x)
    model = KMeans(n_clusters=2, random_state=42, n_init=10).fit(prep.transform(segment_x))
    directory = root / "segmentation_v1/models"
    directory.mkdir(parents=True)
    joblib.dump({"preprocessor": prep, "model": model, "features": features,
                 "canonical_mapping": {0: 0, 1: 1}, "segment_names": {0: "a", 1: "b"},
                 "version": "segmentation_v1", "algorithm": "kmeans"}, directory / "final_model.joblib")
    approvals = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in root.glob("*/models/*.joblib")}
    (root / "trusted-artifacts.json").write_text(json.dumps(approvals))
    return root
