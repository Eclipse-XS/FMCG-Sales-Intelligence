# Data engineering productization V1

PostgreSQL is the executed operational source. The local extractor copies all 18 tables into DuckDB raw storage. dbt builds staging, intermediate, dimensions/facts, and marts. Polars builds published task datasets; Great Expectations validates those artifacts; DVC owns the seven task inputs and seven canonical analytical stages.

Kafka is an optional idempotent replay/DLQ simulation and is not required for batch inference. Airflow remains a discoverable DAG definition, not a deployed scheduler. Airbyte and BigQuery are templates, not executed systems. Raw donor data is immutable; generated operational data, warehouse state, processed data, and canonical artifacts have separate ownership.

Quality layers are not interchangeable: dbt tests relational transformations, Great Expectations tests published datasets, pytest tests code/scientific contracts, and Pydantic validates API envelopes.

