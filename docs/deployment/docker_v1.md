# Docker V1

- Database only: `docker compose up -d`
- Product: `docker compose --profile core up -d --build`
- MLflow: `docker compose --profile mlops up -d --build`
- Observability: `docker compose --profile observability up -d`
- Full local demo: `docker compose --profile full-demo up -d --build`

The API mounts canonical artifacts read-only and does not copy DVC cache/raw data into its image. MLflow metadata uses a separate `mlflow` PostgreSQL database and a persistent artifact volume. Existing database volumes may require the documented one-time database bootstrap because init scripts only run for a new volume. Do not use `down -v` unless intentionally deleting local state.

| Service | Liveness | Readiness | Dependency behavior |
|---|---|---|---|
| PostgreSQL | process | `pg_isready` | data jobs connect explicitly |
| API | `/health` | `/ready` verifies frozen artifacts | MLflow soft; artifacts hard |
| Frontend | nginx response | static index response | starts after API readiness |
| MLflow | process | `/health` plus backend connection | waits for PostgreSQL |
| Prometheus | process | web readiness | starts after API readiness |
| Grafana | `/api/health` | datasource availability | optional profile |
