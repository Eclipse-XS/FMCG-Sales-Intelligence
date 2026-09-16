"""Daily batch orchestration; deploy into an Airflow 2.10+ DAGs directory."""
from __future__ import annotations
from datetime import datetime
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
import subprocess,sys
from pathlib import Path
ROOT=Path("/opt/airflow/project")
def run(*args):
    result=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    if result.returncode:raise AirflowException(result.stderr[-2000:])
@dag(schedule="0 3 * * *",start_date=datetime(2024,1,1),catchup=False,tags=["fmcg","data-platform"])
def fmcg_data_platform():
    @task
    def check_source_database(): run(sys.executable,"src/database/validate_database.py")
    @task
    def replicate_to_warehouse(): run(sys.executable,"src/warehouse/extract_operational.py")
    @task
    def dbt_build(): run(sys.executable,"-m","dbt","build","--project-dir","dbt","--profiles-dir","dbt")
    @task
    def build_datasets(): run(sys.executable,"src/datasets/build_all.py")
    @task
    def quality(): run(sys.executable,"src/quality/validate_datasets.py")
    check_source_database() >> replicate_to_warehouse() >> dbt_build() >> build_datasets() >> quality()
fmcg_data_platform()
