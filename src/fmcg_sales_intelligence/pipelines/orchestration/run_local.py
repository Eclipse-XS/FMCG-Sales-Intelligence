"""Run the fully local, reproducible analytical path after OLTP data is loaded."""
from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT

import subprocess
import sys
import shutil
from pathlib import Path

ROOT = PROJECT_ROOT
PYTHON = sys.executable


def run(*args: str, cwd: Path = ROOT) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def main() -> None:
    run(PYTHON, "src/fmcg_sales_intelligence/pipelines/warehouse/extract_operational.py")
    dbt = shutil.which("dbt") or str(Path(PYTHON).parent / ("dbt.exe" if sys.platform == "win32" else "dbt"))
    run(dbt, "build", "--profiles-dir", ".", cwd=ROOT / "platform" / "dbt")
    run(PYTHON, "src/fmcg_sales_intelligence/pipelines/datasets/build_all.py")
    run(PYTHON, "src/fmcg_sales_intelligence/pipelines/quality/validate_datasets.py")


if __name__ == "__main__":
    main()
