# Technology stack V1

Lifecycle states follow `artifacts/project/technology_registry_v1.json`.

| Technology | Role | State |
|---|---|---|
| Python, pandas, Polars, NumPy | product runtime, model interoperability, dataset construction | ACTIVE_EXECUTED |
| PostgreSQL | operational business source | ACTIVE_EXECUTED |
| DuckDB + dbt | local analytical warehouse and transformations | ACTIVE_EXECUTED |
| dbt tests + Great Expectations + pytest + Pydantic | layered warehouse, dataset, application and API quality | ACTIVE_EXECUTED |
| DVC | data/pipeline/canonical-artifact ownership | ACTIVE_EXECUTED; GitHub + gdrive clean-clone proof passed |
| scikit-learn, CatBoost, lifelines, mlxtend, joblib | frozen classical ML/statistical implementations | ACTIVE_EXECUTED |
| FastAPI, Pydantic, Uvicorn | typed local backend and frozen inference | ACTIVE_EXECUTED |
| React, TypeScript, Vite, ECharts | business dashboard | ACTIVE_EXECUTED_V1_1 |
| MLflow | optional local run tracking/registry, isolated from operational tables | ACTIVE_EXECUTED_LOCAL |
| Prometheus | API metrics collection | ACTIVE_EXECUTED_LOCAL |
| Grafana | engineering observability provisioning | ACTIVE_EXECUTED_LOCAL |
| Kafka | ingestion/replay simulation | ACTIVE_EXECUTED_LOCAL_SIMULATION |
| Airflow | DAG definition and bounded orchestration demo | ACTIVE_EXECUTED_LOCAL_ORCHESTRATION_DEMO |
| Airbyte, BigQuery | future integration/cloud templates | TEMPLATE_ONLY |
| GitHub Actions | fixture-safe CI | ACTIVE_PARTIAL until remote execution |

Not needed: Kubernetes, Spark, Redis, Celery, MinIO, Streamlit, a second registry, and a second charting library. Their roles are absent at current scale. DVC and MLflow do not overlap: DVC owns reproducibility objects; MLflow owns runs and registry metadata.

Polars is preferred for dataset construction and larger transformations. pandas remains appropriate for sklearn/CatBoost/lifelines/mlxtend interoperability and compact reports.
