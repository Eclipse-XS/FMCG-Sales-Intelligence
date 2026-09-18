# System architecture V1

```mermaid
flowchart LR
  S[Company source/export] --> P[Domain pack + adapter]
  P --> C[Canonical contracts v1]
  C --> PG[(PostgreSQL operational)]
  PG --> D[(DuckDB + dbt)]
  D --> Q[Polars builders + GE]
  Q --> V[DVC datasets/artifacts]
  V --> M[ML/analytics cores]
  M --> F[Frozen canonical artifacts]
  F --> API[FastAPI services]
  API --> UI[React business dashboard]
  F --> MF[MLflow run/registry metadata]
  API --> PR[Prometheus]
  PR --> G[Grafana engineering view]
```

The generic package never imports `coca_cola_demo`. Domain packs depend on canonical contracts and are selected at the boundary. Kafka is optional replay simulation; Airflow is a DAG definition; Airbyte and BigQuery are templates. Batch inference is primary, HTTP inference is integration/demo access.

