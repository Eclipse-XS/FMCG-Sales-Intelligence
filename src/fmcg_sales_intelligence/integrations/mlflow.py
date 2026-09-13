from __future__ import annotations

import json
import re

from ..engine import EngineError, Model, Predictor, Signature


class MLflowRegistry:
    """Native MLflow versions/signatures; load only explicitly approved immutable URIs.

    approval is deployment configuration, never request input. MLflow storage and
    writers must be trusted: sklearn serialization is executable Python.
    """
    def __init__(self, tracking_uri: str, approved: dict[str, Signature]):
        import mlflow
        import mlflow.sklearn
        self.mlflow = mlflow
        self.client = mlflow.MlflowClient(tracking_uri=tracking_uri, registry_uri=tracking_uri)
        self.tracking_uri = tracking_uri
        self.approved = dict(approved)
        self._models = {}
        for uri in self.approved:
            if not re.fullmatch(r"models:/[A-Za-z0-9_.-]+/[0-9]+", uri):
                raise ValueError("Approval requires an immutable models:/name/numeric-version URI")

    def resolve(self, name, version=None):
        matches = [u for u in self.approved if u.split("/")[1] == name]
        if version is None:
            if len(matches) > 1:
                raise EngineError("VERSION_REQUIRED", "Select an explicit immutable model version")
            if len(matches) == 1:
                version = matches[0].split("/")[2]
        uri = f"models:/{name}/{version}"
        if uri not in self.approved:
            raise EngineError("MODEL_NOT_FOUND", "Unknown or unapproved model/version", 404)
        if uri in self._models:
            return self._models[uri]
        signature = self.approved[uri]
        try:
            # MLflow uses process-global URI configuration: initialize once at startup.
            self.mlflow.set_tracking_uri(self.tracking_uri)
            self.mlflow.set_registry_uri(self.tracking_uri)
            info = self.mlflow.models.get_model_info(uri)
            if info.signature is None or info.signature.inputs is None or info.signature.outputs is None:
                raise ValueError("MLflow input and output signatures are required")
            if info.signature.inputs.input_names() != [f.name for f in signature.features]:
                raise ValueError("MLflow input names/order differ from approved signature")
            expected_types = {"number": {"double", "float", "long", "integer"},
                              "integer": {"long", "integer"}, "string": {"string"},
                              "boolean": {"boolean"}, "datetime": {"datetime"}}
            for column, feature in zip(info.signature.inputs.inputs, signature.features):
                if str(column.type) not in expected_types[feature.dtype]:
                    # MLflow DataType.__str__ may be 'DataType.double'.
                    if str(column.type).split(".")[-1] not in expected_types[feature.dtype]:
                        raise ValueError("MLflow input type differs from approved signature")
            metadata = info.metadata or {}
            stored = Signature.from_dict(metadata["engine_signature"])
            if stored != signature:
                raise ValueError("Logged and approved engine signatures differ")
            estimator = self.mlflow.sklearn.load_model(uri)
            probabilities = metadata.get("engine_task") == "classification"
            result = Model(name, str(version), metadata["engine_task"], signature,
                           Predictor(estimator, probabilities=probabilities),
                           ("predictions", "probabilities", "classes") if probabilities else ("predictions",),
                           {"uri": uri, "run_id": info.run_id, "registry": "mlflow"})
        except Exception:
            # Diagnostics are logged server-side; do not expose paths/credentials.
            import logging
            logging.getLogger(__name__).exception("Approved MLflow model unavailable: %s", uri)
            result = Model(name, str(version), "scoring", signature, None,
                           provenance={"uri": uri, "registry": "mlflow"},
                           unavailable_reason="Approved artifact could not be loaded or validated")
        self._models[uri] = result
        return result

    def metadata(self):
        return [self.resolve(u.split("/")[1], u.split("/")[2]).metadata() for u in self.approved]


def register_sklearn(tracking_uri, name, estimator, signature: Signature, example, *, task):
    """Operator Python API for an already fitted, reviewed sklearn Pipeline."""
    import mlflow
    import mlflow.sklearn
    from sklearn.pipeline import Pipeline
    if not isinstance(estimator, Pipeline):
        raise ValueError("Register a Pipeline bundling training-time preprocessing")
    if task not in {"regression", "classification", "forecasting", "clustering", "scoring"}:
        raise ValueError("Unsupported task")
    # Validate compatibility before logging artifacts or allocating a version.
    Model(name, "1", task, signature, Predictor(estimator, probabilities=task == "classification"))
    frame = signature.validate(example)
    predictions = estimator.predict(frame)
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_registry_uri(tracking_uri)
    mlflow.set_experiment("tabular-integration")
    with mlflow.start_run():
        info = mlflow.sklearn.log_model(
            estimator, artifact_path="model", signature=mlflow.models.infer_signature(frame, predictions),
            input_example=frame.head(3), metadata={"engine_signature": json.loads(json.dumps(signature.metadata())),
                                                 "engine_task": task},
        )
        version = mlflow.register_model(info.model_uri, name)
    return f"models:/{name}/{version.version}"
