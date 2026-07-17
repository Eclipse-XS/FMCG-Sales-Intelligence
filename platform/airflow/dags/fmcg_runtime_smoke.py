"""Bounded non-scientific runtime proof for local Airflow discovery/execution."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from airflow.decorators import dag, task
from airflow.exceptions import AirflowException


ROOT = Path(os.environ.get("FSI_PROJECT_ROOT", Path(__file__).resolve().parents[3])).resolve()


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["fmcg", "runtime-smoke"])
def fmcg_runtime_smoke():
    @task
    def verify_frozen_evidence() -> dict[str, str]:
        if not (ROOT / "pyproject.toml").is_file():
            raise AirflowException("FSI_PROJECT_ROOT does not identify the project root")
        manifest = ROOT / "artifacts" / "canonical" / "segmentation_v1" / "manifest.json"
        metrics = ROOT / "artifacts" / "segmentation_v1_metrics.json"
        if not manifest.is_file() or not metrics.is_file():
            raise AirflowException("Frozen segmentation evidence is unavailable")
        manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
        metrics_payload = json.loads(metrics.read_text(encoding="utf-8"))
        if manifest_payload.get("selected_k") != 3:
            raise AirflowException("Frozen segmentation k changed")
        if round(float(metrics_payload.get("selected_silhouette")), 10) != 0.3307169762:
            raise AirflowException("Frozen segmentation silhouette changed")
        return {"status": "PASS", "training_executed": "false"}

    verify_frozen_evidence()


fmcg_runtime_smoke()
