from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable, Protocol
from uuid import uuid4

import numpy as np
import pandas as pd

from .contracts import EngineError, Signature
from .data import DomainRegistry, read_source

LOGGER = logging.getLogger(__name__)


class Runtime(Protocol):
    def execute(self, frame: pd.DataFrame) -> dict[str, Any]: ...


class Predictor:
    """Prediction/scoring only; rule mining and training are separate jobs."""
    def __init__(self, estimator, *, probabilities=False, clip_lower=None):
        self.estimator, self.probabilities, self.clip_lower = estimator, probabilities, clip_lower
        if not callable(getattr(estimator, "predict", None)):
            raise ValueError("Estimator must implement predict")
        if probabilities and not callable(getattr(estimator, "predict_proba", None)):
            raise ValueError("Probability scoring requires predict_proba")

    def execute(self, frame):
        predictions = np.asarray(self.estimator.predict(frame))
        if self.clip_lower is not None:
            predictions = np.maximum(predictions, self.clip_lower)
        result = {"predictions": predictions.tolist()}
        if self.probabilities:
            result["probabilities"] = np.asarray(self.estimator.predict_proba(frame)).tolist()
            result["classes"] = np.asarray(self.estimator.classes_).tolist()
        return result


@dataclass(frozen=True)
class Model:
    name: str
    version: str
    task: str
    signature: Signature
    runtime: Runtime | None
    output_schema: tuple[str, ...] = ("predictions",)
    provenance: dict = field(default_factory=dict)
    unavailable_reason: str | None = None

    def __post_init__(self):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", self.name) or not re.fullmatch(r"[A-Za-z0-9_.-]+", self.version):
            raise ValueError("Invalid model identity")
        if self.task not in {"regression", "classification", "forecasting", "clustering", "scoring"}:
            raise ValueError("Unsupported online task; analytical jobs use scientific entry points")
        if not self.output_schema or len(set(self.output_schema)) != len(self.output_schema):
            raise ValueError("Output schema must declare distinct result fields")
        estimator = getattr(self.runtime, "estimator", None)
        names = getattr(estimator, "feature_names_in_", None)
        if names is not None and list(names) != [f.name for f in self.signature.features]:
            raise ValueError("Estimator feature names/order differ from signature")
        count = getattr(estimator, "n_features_in_", None)
        if count is not None and count != len(self.signature.features):
            raise ValueError("Estimator feature count differs from signature")

    def metadata(self):
        return {"name": self.name, "version": self.version, "task": self.task,
                "ready": self.runtime is not None, "input_schema": self.signature.metadata(),
                "output_schema": list(self.output_schema), "provenance": self.provenance,
                "diagnostic": self.unavailable_reason}


class Registry(Protocol):
    def resolve(self, name: str, version: str | None = None) -> Model: ...
    def metadata(self) -> list[dict]: ...


class MemoryRegistry:
    """Process-local deployment catalog; MLflow owns persistent model versions."""
    def __init__(self):
        self._models: dict[tuple[str, str], Model] = {}

    def register(self, model: Model):
        key = (model.name, model.version)
        if key in self._models:
            raise EngineError("MODEL_CONFLICT", "Model version already registered", 409)
        self._models[key] = model

    def resolve(self, name, version=None):
        if version is None:
            matches = [m for (n, _), m in self._models.items() if n == name]
            if len(matches) > 1:
                raise EngineError("VERSION_REQUIRED", "Select an explicit immutable model version")
            if matches:
                return matches[0]
        if (name, version) not in self._models:
            raise EngineError("MODEL_NOT_FOUND", "Unknown model/version", 404)
        return self._models[name, version]

    def metadata(self):
        return [m.metadata() for m in self._models.values()]


class Engine:
    def __init__(self, registry: Registry, domains: DomainRegistry | None = None, *, max_batch=1000,
                 observe: Callable[[dict], None] | None = None):
        self.registry, self.domains = registry, domains or DomainRegistry()
        if max_batch < 1:
            raise ValueError("max_batch must be positive")
        self.max_batch, self.observe = max_batch, observe

    def validate(self, name, source, *, version=None, domain=None):
        model = self.registry.resolve(name, version)
        frame = read_source(source)
        if not 1 <= len(frame) <= self.max_batch:
            raise EngineError("INVALID_BATCH", f"Batch size must be between 1 and {self.max_batch}")
        if domain is not None:
            frame = self.domains.get(domain).normalize(frame)
        return model, model.signature.validate(frame)

    def infer(self, name, source, *, version=None, domain=None, request_id=None):
        model, frame = self.validate(name, source, version=version, domain=domain)
        if model.runtime is None:
            raise EngineError("MODEL_UNAVAILABLE", "Registered model is unavailable", 503)
        identity, started = request_id or str(uuid4()), perf_counter()
        try:
            output = model.runtime.execute(frame)
            if set(output) != set(model.output_schema):
                raise ValueError("Runtime output differs from declared schema")
            if len(output.get("predictions", [])) != len(frame):
                raise ValueError("Runtime returned wrong row count")
            if "probabilities" in output:
                probabilities = np.asarray(output["probabilities"], dtype=float)
                if (probabilities.ndim != 2 or probabilities.shape != (len(frame), len(output["classes"]))
                        or not np.isfinite(probabilities).all() or (probabilities < 0).any()
                        or (probabilities > 1).any() or not np.allclose(probabilities.sum(axis=1), 1)):
                    raise ValueError("Invalid probability matrix")
            json.dumps(output, allow_nan=False)
        except Exception as exc:
            LOGGER.exception("Model execution failed request_id=%s", identity)
            raise EngineError("EXECUTION_FAILED", "Model execution failed", 500) from exc
        metadata = {"model": model.name, "version": model.version, "task": model.task,
                    "rows": len(frame), "domain": domain, "request_id": identity,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "duration_seconds": perf_counter() - started, "provenance": model.provenance}
        if self.observe:
            try:
                self.observe(metadata)
            except Exception:
                LOGGER.exception("Observer failed request_id=%s", identity)
        return {**output, "metadata": metadata}
