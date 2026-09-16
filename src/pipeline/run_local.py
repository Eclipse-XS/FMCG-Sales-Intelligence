"""Run the fully local, reproducible analytical path after OLTP data is loaded."""
from __future__ import annotations

import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable


def run(*args: str, cwd: Path = ROOT) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def main() -> None:
    run(PYTHON, "src/warehouse/extract_operational.py")
    dbt = shutil.which("dbt") or str(Path(PYTHON).parent / ("dbt.exe" if sys.platform == "win32" else "dbt"))
    run(dbt, "build", "--profiles-dir", ".", cwd=ROOT / "dbt")
    run(PYTHON, "src/datasets/build_all.py")
    run(PYTHON, "src/quality/validate_datasets.py")


if __name__ == "__main__":
    main()
