from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np
import pandas as pd


class EngineError(Exception):
    def __init__(self, code: str, message: str, status: int = 422):
        super().__init__(message)
        self.code, self.status = code, status


@dataclass(frozen=True)
class Feature:
    name: str
    dtype: Literal["number", "integer", "string", "boolean", "datetime"]
    nullable: bool = False
    categories: tuple | None = None
    coerce: bool = False

    def __post_init__(self):
        if not self.name or self.dtype not in {"number", "integer", "string", "boolean", "datetime"}:
            raise ValueError("Invalid feature definition")
        if self.categories is not None:
            object.__setattr__(self, "categories", tuple(self.categories))


@dataclass(frozen=True)
class Signature:
    features: tuple[Feature, ...]
    forbidden: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "features", tuple(self.features))
        object.__setattr__(self, "forbidden", tuple(self.forbidden))
        names = [f.name for f in self.features]
        if not names or len(names) != len(set(names)) or set(names) & set(self.forbidden):
            raise ValueError("Signature requires distinct, non-forbidden feature names")

    def metadata(self):
        return {"features": [asdict(f) for f in self.features], "forbidden": list(self.forbidden)}

    @classmethod
    def from_dict(cls, payload):
        return cls(tuple(Feature(**f) for f in payload["features"]), tuple(payload.get("forbidden", [])))

    def validate(self, frame: pd.DataFrame) -> pd.DataFrame:
        if not frame.columns.is_unique:
            raise EngineError("INVALID_SCHEMA", "Duplicate column names")
        names = [f.name for f in self.features]
        supplied = set(frame.columns)
        if supplied & set(self.forbidden):
            raise EngineError("FORBIDDEN_FEATURE", f"Outcome/future fields: {sorted(supplied & set(self.forbidden))}")
        if set(names) - supplied:
            raise EngineError("MISSING_FEATURE", f"Missing required features: {sorted(set(names) - supplied)}")
        if supplied - set(names):
            raise EngineError("UNEXPECTED_FEATURE", f"Unexpected features: {sorted(supplied - set(names))}")
        result = frame.loc[:, names].copy()
        for feature in self.features:
            s = result[feature.name]
            if not feature.nullable and s.isna().any():
                raise EngineError("NULL_FEATURE", f"Feature {feature.name} is not nullable")
            values = s.dropna()
            try:
                if feature.dtype in {"number", "integer"}:
                    if values.map(lambda v: isinstance(v, (bool, np.bool_))).any():
                        raise ValueError("boolean is not numeric")
                    if not feature.coerce and not pd.api.types.is_numeric_dtype(values):
                        raise ValueError("numeric type required")
                    numeric = pd.to_numeric(s, errors="raise")
                    if not np.isfinite(numeric.dropna().to_numpy(dtype=float)).all():
                        raise ValueError("finite numbers required")
                    if feature.dtype == "integer" and (numeric.dropna() % 1 != 0).any():
                        raise ValueError("fractional integer")
                    result[feature.name] = numeric
                elif feature.dtype == "string":
                    if not feature.coerce and not values.map(lambda v: isinstance(v, str)).all():
                        raise ValueError("string required")
                    result[feature.name] = s.astype("string") if feature.coerce else s
                elif feature.dtype == "boolean":
                    if not values.map(lambda v: isinstance(v, (bool, np.bool_))).all():
                        raise ValueError("boolean required (no truthiness conversion)")
                elif feature.dtype == "datetime":
                    if not feature.coerce and not pd.api.types.is_datetime64_any_dtype(s):
                        raise ValueError("datetime type required")
                    result[feature.name] = pd.to_datetime(s, errors="raise", utc=True)
                if feature.categories is not None and not result[feature.name].dropna().isin(feature.categories).all():
                    raise ValueError("unknown category")
            except (TypeError, ValueError, OverflowError) as exc:
                raise EngineError("INVALID_FEATURE", f"Feature {feature.name}: {exc}") from exc
        return result
