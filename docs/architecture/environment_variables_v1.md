# Environment variables V1

| Variable | Service | Required | Secret | Default/purpose |
|---|---|---|---|---|
| `POSTGRES_*` / `DATABASE_URL` | PostgreSQL/data jobs | local | password field | local business database connection |
| `FSI_ACTIVE_DOMAIN_PACK` | API | no | no | `coca_cola_demo` |
| `FSI_ARTIFACT_ROOT` | API | no | no | trusted frozen artifacts |
| `FSI_API_HOST`, `FSI_API_PORT` | API | no | no | `0.0.0.0:8000` |
| `FSI_CORS_ORIGINS` | API | no | no | explicit local frontend origins |
| `FSI_MLFLOW_TRACKING_URI` | CLI/API metadata | no | no | local MLflow endpoint |
| `FSI_MLFLOW_REQUIRED_FOR_READINESS` | API | no | no | false; serving uses canonical artifacts |
| `MLFLOW_DB`, `MLFLOW_PORT` | MLflow | no | no | isolated metadata database and port |
| `FRONTEND_PORT` | dashboard | no | no | 8080 |
| `PROMETHEUS_PORT` | observability | no | no | 9090 |
| `GRAFANA_ADMIN_PASSWORD` | Grafana | local override | yes | development fallback only |

Real secrets belong outside Git. `.env.example` contains local placeholders only.

