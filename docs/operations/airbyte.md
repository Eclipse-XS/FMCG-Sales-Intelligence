# Airbyte replication

Airbyte is configured, not runtime-executed. A complete local Airbyte deployment requires additional services and substantially more disk/RAM than this developer profile provides. The executable local equivalent is `src/fmcg_sales_intelligence/pipelines/warehouse/extract_operational.py`, which refreshes raw DuckDB tables and Parquet replicas idempotently.

For an Airbyte deployment, create the PostgreSQL source and BigQuery destination using `platform/airbyte/postgres_to_bigquery.json`. Use batch watermark extraction initially. Logical CDC requires PostgreSQL WAL logical replication configuration and a replication user; neither is enabled implicitly.
