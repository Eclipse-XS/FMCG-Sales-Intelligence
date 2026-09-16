# Airflow orchestration

`dags/fmcg_platform.py` defines a DAG with the dependency chain `extract → dbt build → build datasets → Great Expectations → publish report`. It is importable by an Airflow installation that mounts the repository at `/opt/airflow/project` and supplies the same Python dependencies.

Airflow was not deployed in this developer environment. There is no execution claim, scheduler claim, or historical DAG-run claim. The individual commands are executable locally and are the supported validation path until an Airflow deployment is provisioned.
