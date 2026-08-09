# Portfolio architecture V1.3

```mermaid
flowchart TB
  S[Company / source systems] --> A[Adapter + replaceable domain pack]
  A --> C[Versioned canonical contracts]
  C --> I[Ingestion + validation]
  I --> P[(PostgreSQL operational schema)]
  P --> W[(DuckDB + dbt warehouse)]
  W --> D[Processed task datasets]
  D --> M[Seven frozen analytical cores]
  M --> V[DVC artifacts + MLflow metadata]
  V --> API[FastAPI]
  API --> DOCS[FastAPI / Swagger docs]
  P --> G[Grafana Analytical & Operational Dashboards]
  K[Kafka local replay] -. optional event ingress .-> I
  AF[Airflow bounded demo] -. batch orchestration .-> I
  API -. operational metrics .-> PR[Prometheus]
  PR --> G
```

The solid path is the primary batch-to-product lineage. Kafka is an optional isolated replay simulation. Airflow demonstrates bounded orchestration and does not imply a persistent deployment. Prometheus and Grafana observe the API; they are not inference dependencies.

Company-specific mappings live under `config/domains`. Scientific implementations do not depend on the Coca-Cola demo pack. PostgreSQL remains operational; derived features, predictions and analytical outputs remain outside its schema.
