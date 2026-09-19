"""Daily batch orchestration; deploy into an Airflow 2.10+ DAGs directory."""
from __future__ import annotations
from datetime import datetime
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
import os
import subprocess
import sys
from pathlib import Path
ROOT=Path(os.environ.get("FSI_PROJECT_ROOT", Path(__file__).resolve().parents[3])).resolve()
def run(*args):
    if not (ROOT / "pyproject.toml").is_file():
        raise AirflowException("FSI_PROJECT_ROOT does not identify the project root")
    result=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    if result.returncode:
        raise AirflowException(result.stderr[-2000:])
@dag(schedule="0 3 * * *",start_date=datetime(2024,1,1),catchup=False,tags=["fmcg","data-platform"])
def fmcg_data_platform():
    @task
    def check_source_database(): run(sys.executable,"src/fmcg_sales_intelligence/pipelines/persistence/validate_database.py")
    @task
    def replicate_to_warehouse(): run(sys.executable,"src/fmcg_sales_intelligence/pipelines/warehouse/extract_operational.py")
    @task
    def dbt_build(): run(sys.executable,"-m","dbt","build","--project-dir","platform/dbt","--profiles-dir","platform/dbt")
    @task
    def build_datasets(): run(sys.executable,"src/fmcg_sales_intelligence/pipelines/datasets/build_all.py")
    @task
    def quality(): run(sys.executable,"src/fmcg_sales_intelligence/pipelines/quality/validate_datasets.py")
    check_source_database() >> replicate_to_warehouse() >> dbt_build() >> build_datasets() >> quality()
fmcg_data_platform()
