from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import pandas as pd

from .contracts import EngineError, Signature


def read_source(source) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        return source.copy()
    if isinstance(source, list):
        if not all(isinstance(row, dict) for row in source):
            raise EngineError("INVALID_SOURCE", "Rows must be objects")
        # A missing cell in one row must not masquerade as an explicitly nullable cell.
        if source and any(set(row) != set(source[0]) for row in source):
            raise EngineError("MISSING_FEATURE", "All rows must contain the same feature keys")
        return pd.DataFrame(source)
    path = Path(source)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise EngineError("INVALID_SOURCE", "Supported sources: DataFrame, records, CSV, Parquet")


@dataclass(frozen=True)
class DomainPack:
    name: str
    version: str
    signature: Signature
    mapping: dict[str, str] = field(default_factory=dict)
    scales: dict[str, float] = field(default_factory=dict)
    transform: Callable[[pd.DataFrame], pd.DataFrame] | None = None

    def normalize(self, frame: pd.DataFrame) -> pd.DataFrame:
        if not frame.columns.is_unique or len(set(self.mapping.values())) != len(self.mapping.values()):
            raise EngineError("INVALID_MAPPING", "Duplicate source or destination columns")
        if set(self.mapping) - set(frame.columns):
            raise EngineError("INVALID_MAPPING", f"Missing mapped columns: {sorted(set(self.mapping) - set(frame.columns))}")
        # Do not project away unexpected fields: validation must see leakage/extras.
        frame = frame.rename(columns=self.mapping).copy()
        frame = self.signature.validate(frame)
        for name, factor in self.scales.items():
            if name not in frame or not pd.api.types.is_numeric_dtype(frame[name]):
                raise EngineError("INVALID_TRANSFORM", f"Scale requires numeric feature {name}")
            frame[name] = frame[name] * factor
        if self.transform:
            frame = self.transform(frame.copy())
        return frame

    def metadata(self):
        return {"name": self.name, "version": self.version, "input_schema": self.signature.metadata(),
                "mapping": self.mapping, "scales": self.scales}


class DomainRegistry:
    def __init__(self):
        self._packs = {}

    def register(self, pack: DomainPack):
        if pack.name in self._packs:
            raise EngineError("DOMAIN_CONFLICT", "Domain already registered", 409)
        self._packs[pack.name] = pack

    def get(self, name: str) -> DomainPack:
        if name not in self._packs:
            raise EngineError("DOMAIN_NOT_FOUND", "Unknown domain pack", 404)
        return self._packs[name]

    def metadata(self):
        return [p.metadata() for p in self._packs.values()]
