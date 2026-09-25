# Version compatibility V1

| Component | Validated version |
|---|---|
| Python | 3.13.5 |
| PostgreSQL | 17.11 |
| DVC | 3.63.0 |
| DuckDB / dbt-core / dbt-duckdb | 1.5.5 / 1.12.5 / 1.11.0 |
| Polars / pandas / NumPy | 1.44.2 / 3.0.5 / 2.5.3 |
| scikit-learn / CatBoost | 1.7.2 / 1.2.8 |
| lifelines / mlxtend | 0.30.0 / 0.23.4 |
| Great Expectations | 1.23.0 |
| FastAPI / Pydantic / Uvicorn | 0.116.1 / 2.11.7 / 0.35.0 |
| MLflow | 3.16.1, isolated container |
| Docker / Compose | 29.7.2 / 5.5.1 |
| Grafana | 11.5.2 (11 dashboards-as-code) |
| Prometheus | 3.5.0 |

MLflow is isolated from the frozen scientific environment, which must retain pandas 3.0.5 and PyArrow 25.0.1. MLflow 3.16.1 also avoids the PostgreSQL model-alias type mismatch observed with 3.3.2. No scientific-runtime upgrades were performed.
