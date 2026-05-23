from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ..common.paths import project_path


class DomainPackRegistry:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else project_path("domain_packs")

    def list(self) -> list[dict[str, Any]]:
        profiles = []
        for path in sorted(self.root.glob("*/profile.yaml")):
            profiles.append(self._safe_profile(path))
        return profiles

    def get(self, profile_id: str) -> dict[str, Any]:
        for profile in self.list():
            if profile["profile_id"] == profile_id:
                return profile
        raise KeyError(profile_id)

    @staticmethod
    def _safe_profile(path: Path) -> dict[str, Any]:
        profile = yaml.safe_load(path.read_text(encoding="utf-8"))
        allowed = {
            "profile_id",
            "profile_version",
            "display_name",
            "source_system_type",
            "currency",
            "timezone",
            "disclaimer",
            "contracts",
            "labels",
            "theme",
        }
        missing = {"profile_id", "profile_version", "display_name", "contracts"} - set(profile)
        if missing:
            raise ValueError(f"Invalid domain pack {path.name}: missing {sorted(missing)}")
        return {key: value for key, value in profile.items() if key in allowed}
