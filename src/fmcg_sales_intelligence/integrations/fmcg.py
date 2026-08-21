from __future__ import annotations

import numpy as np

from ..engine import Feature, Model, Signature
from ..product.serving.inference import FORBIDDEN_FORECAST, FORBIDDEN_STOCKOUT, ForecastService, StockoutService


class FrozenRuntime:
    def __init__(self, service, output):
        self.service, self.output = service, output

    def execute(self, frame):
        values = self.service.predict(frame.to_dict(orient="records"))
        return {"predictions": [row[self.output] for row in values]}


def register_frozen_models(target_registry, frozen):
    """FMCG bridge retains canonical feature prep, clipping and risk threshold."""
    specs = [("forecasting", ForecastService, "predicted_units", "forecasting", FORBIDDEN_FORECAST),
             ("stockout_classification", StockoutService, "stockout_probability", "classification", FORBIDDEN_STOCKOUT)]
    for name, service, output, task, forbidden in specs:
        record = frozen.get(name)
        if not record.ready:
            continue
        bundle = record.bundle
        categorical = set(bundle.get("categorical", []))
        # Frozen models intentionally accept nullable numeric inputs through their
        # fitted preprocessing and string-coerce categorical identifiers.
        features = tuple(Feature(f, "string" if f in categorical else "number", nullable=True,
                                 coerce=f in categorical) for f in bundle["features"])
        signature = Signature(features, tuple(sorted(forbidden)))
        runtime = FrozenRuntime(service(frozen), output)
        target_registry.register(Model(name, record.version, task, signature, runtime,
                                       provenance={"sha256": record.fingerprint, "scientific": "frozen_v1"}))


class ForecastEstimator:
    """Reviewed adapter for a canonical fitted regressor, without retraining."""
    def __init__(self, bundle):
        self.bundle = bundle

    def predict(self, frame):
        frame = frame.copy()
        for column in self.bundle["categorical"]:
            frame[column] = frame[column].fillna("__MISSING__").astype(str)
        return np.maximum(self.bundle["model"].predict(frame), self.bundle.get("clip_lower", 0))
