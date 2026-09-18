# Airflow orchestration

`dags/fmcg_platform.py` defines a DAG with the dependency chain `source check → extract → dbt build → build datasets → quality`. The project root is resolved from `FSI_PROJECT_ROOT`, with the repository containing the DAG as the local default; no machine-specific absolute path is embedded.

Airflow was not deployed in this developer environment. There is no execution claim, scheduler claim, or historical DAG-run claim. The individual commands are executable locally and are the supported validation path until an Airflow deployment is provisioned.

The module is syntax-checked in pytest. A real Airflow import/parse and task run remain deployment checks because Apache Airflow is intentionally not added to the product runtime environment.
