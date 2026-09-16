from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
import math
from decimal import Decimal
from pathlib import Path
from typing import Any


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Readiness(str, Enum):
    READY = "READY"
    READY_WITH_LIMITATIONS = "READY_WITH_LIMITATIONS"
    NOT_READY = "NOT_READY"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class EDARequest:
    task: str
    dataset_path: Path | None = None
    persist: bool = True


@dataclass
class Finding:
    code: str
    severity: Severity
    message: str
    metric: float | int | None = None
    recommendation: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetIdentity:
    logical_name: str
    path: str
    size_bytes: int
    content_sha256: str
    schema_sha256: str
    row_count: int
    schema: dict[str, str]


@dataclass
class ArtifactReference:
    kind: str
    path: str


@dataclass
class EDAResult:
    run_id: str
    analysis_type: str
    generated_at: str
    status: str
    datasets: list[DatasetIdentity]
    metrics: dict[str, Any]
    profile: dict[str, Any]
    findings: list[Finding]
    readiness: dict[str, Readiness]
    artifacts: list[ArtifactReference] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        def clean(value: Any) -> Any:
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, Path):
                return str(value)
            if isinstance(value, (date, datetime)):
                return value.isoformat()
            if isinstance(value, float) and not math.isfinite(value):
                return None
            if isinstance(value, Decimal):
                return float(value)
            if isinstance(value, dict):
                return {k: clean(v) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return [clean(v) for v in value]
            return value
        return clean(asdict(self))


@dataclass
class RunComparison:
    run_a: str
    run_b: str
    task: str
    identical_data: bool
    schema: dict[str, Any]
    metric_changes: dict[str, dict[str, Any]]
    findings: list[Finding]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_a": self.run_a, "run_b": self.run_b, "task": self.task,
            "identical_data": self.identical_data, "schema": self.schema,
            "metric_changes": self.metric_changes,
            "findings": [asdict(x) | {"severity": x.severity.value} for x in self.findings],
        }
