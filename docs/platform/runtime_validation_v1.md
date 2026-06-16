# Platform runtime validation V1.1

| Component | Evidence | Status |
|---|---|---|
| Kafka | Existing deterministic producer, schema validator, idempotent consumer writes and DLQ code inspected; `docker compose --profile streaming up -d` failed because the Docker Desktop Linux engine pipe was unavailable. No runtime delivery claim is made. | ACTIVE_PARTIAL / runtime BLOCKED_ENVIRONMENT |
| Airflow | DAG source parses as Python, expected five-task dependency chain is present, and project root is environment-driven rather than absolute. Airflow is intentionally absent, so scheduler discovery/task execution was not claimed. | IMPLEMENTED_NOT_RUNTIME_VERIFIED |
| Airbyte | Connector configuration only; no sync or server deployed. | TEMPLATE_ONLY |
| BigQuery | dbt target template only; no credentials, dataset or cloud execution. | TEMPLATE_ONLY |

Kafka remains optional and isolated from canonical `fmcg.sales`. Re-run the documented producer/consumer/idempotency/DLQ smoke when Docker Desktop is available. Airflow runtime validation requires a deliberate Airflow environment and must not retrain frozen models.
