from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from ..common.paths import project_path


@dataclass(frozen=True)
class ContractValidation:
    contract_id: str
    contract_version: str
    row_count: int
    required_columns_found: list[str]
    missing_required_columns: list[str]
    unexpected_columns: list[str]
    null_failures: dict[str, int]
    duplicate_key_count: int
    status: str

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class ContractRegistry:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        contracts = payload.get("contracts", [])
        self._contracts = {item["contract_id"]: item for item in contracts}
        versions = [(x["contract_id"], x["contract_version"]) for x in contracts]
        if len(versions) != len(set(versions)):
            raise ValueError("Contract id/version pairs must be unique")

    def list(self) -> list[dict[str, Any]]:
        return list(self._contracts.values())

    def get(self, contract_id: str) -> dict[str, Any]:
        if contract_id not in self._contracts:
            raise KeyError(contract_id)
        return self._contracts[contract_id]

    def validate(self, contract_id: str, frame: pd.DataFrame) -> ContractValidation:
        contract = self.get(contract_id)
        required = [field["name"] for field in contract["fields"] if field.get("required", False)]
        allowed = [field["name"] for field in contract["fields"]]
        missing = sorted(set(required) - set(frame.columns))
        found = sorted(set(required) & set(frame.columns))
        unexpected = sorted(set(frame.columns) - set(allowed))
        null_failures = {
            name: int(frame[name].isna().sum())
            for name in required
            if name in frame and frame[name].isna().any()
        }
        key = contract["business_key"]
        duplicate_count = int(frame.duplicated(key).sum()) if not missing and set(key) <= set(frame) else 0
        status = "PASS" if not missing and not null_failures and duplicate_count == 0 else "FAIL"
        return ContractValidation(
            contract_id,
            contract["contract_version"],
            len(frame),
            found,
            missing,
            unexpected,
            null_failures,
            duplicate_count,
            status,
        )


def load_registry(path: str | Path | None = None) -> ContractRegistry:
    registry_path = Path(path) if path else project_path("contracts", "registry_v1.yaml")
    return ContractRegistry(yaml.safe_load(registry_path.read_text(encoding="utf-8")))
