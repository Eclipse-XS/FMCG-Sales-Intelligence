# Local ports V1

| Service | Port | Profile/state |
|---|---:|---|
| PostgreSQL | 55432 | default, active |
| FastAPI | 8000 | `core` / `full-demo` |
| Grafana | 3001 | `observability` (primary analytics UI) |
| MLflow | 5000 | `mlops` / `full-demo` |
| Kafka broker | 9094 | `streaming` |
| Kafka UI | 8088 | `streaming` |
| Prometheus | 9090 | `observability` / `full-demo` |


Airflow and Airbyte expose no validated local runtime port in this repository. Port 5432 is intentionally avoided on the host.

