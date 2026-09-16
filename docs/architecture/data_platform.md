# Data platform architecture

```mermaid
flowchart LR
  PG[Operational PostgreSQL] --> EX[Python batch extractor]
  EX --> RAW[DuckDB raw replica]
  RAW --> DBT[dbt: staging / intermediate / marts]
  DBT --> FE[Polars feature builders]
  FE --> PQ[Versioned Parquet datasets]
  PQ --> GE[Great Expectations]
  PG --> K[Kafka replay, isolated streaming schema]
  AF[Airflow DAG] --> EX
  AF --> DBT
  AF --> FE
  AF --> GE
  PG --> G[Grafana]
```

DuckDB is the executed local analytical warehouse fallback. BigQuery is configured but not executed without credentials. Airbyte’s role is PostgreSQL-to-warehouse replication; the local extractor executes the same bounded batch responsibility where an Airbyte server is unavailable.
