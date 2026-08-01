"""Non-destructive release readiness summary for local demonstrations."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
from fmcg_sales_intelligence.product.contracts import load_registry
from fmcg_sales_intelligence.product.domains import DomainPackRegistry
from fmcg_sales_intelligence.product.serving import FrozenModelRegistry
from fmcg_sales_intelligence.product.serving.segment_membership import SegmentMembershipService


def _http_status(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return str(response.status)
    except (OSError, urllib.error.URLError):
        return "not_running"


def _dvc_status(root: Path) -> str:
    executable = shutil.which("dvc") or str(Path(sys.executable).with_name("dvc.exe" if sys.platform == "win32" else "dvc"))
    try:
        result = subprocess.run(
            [executable, "status"], cwd=root, capture_output=True, text=True,
            timeout=20, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    return "clean" if result.returncode == 0 and "up to date" in result.stdout.lower() else "attention_required"


def main() -> int:
    models = FrozenModelRegistry(PROJECT_ROOT / "artifacts" / "canonical")
    segment = SegmentMembershipService(PROJECT_ROOT / "artifacts" / "canonical")
    result = {
        "package_import": "PASS",
        "contracts": len(load_registry().list()),
        "domain_packs": [item["profile_id"] for item in DomainPackRegistry().list()],
        "canonical_artifacts_present": (PROJECT_ROOT / "artifacts" / "canonical").is_dir(),
        "forecasting_loadable": models.get("forecasting").bundle is not None,
        "stockout_loadable": models.get("stockout_classification").bundle is not None,
        "segmentation_loadable": bool(segment.features),
        "dvc": _dvc_status(PROJECT_ROOT),
        "api_health": _http_status("http://localhost:8000/health"),
        "api_ready": _http_status("http://localhost:8000/ready"),
        "mlflow": _http_status("http://localhost:5000/health"),
        "dashboard": _http_status("http://localhost:8080"),
    }
    print(json.dumps(result, indent=2))
    required = (result["canonical_artifacts_present"], result["forecasting_loadable"], result["stockout_loadable"], result["segmentation_loadable"])
    return 0 if all(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
