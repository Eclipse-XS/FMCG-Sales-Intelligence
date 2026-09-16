# Grafana

Start Grafana with `docker compose --profile observability up -d`. It is provisioned with a PostgreSQL datasource and a Platform Health dashboard definition. The datasource reads credentials from Compose environment interpolation; change defaults in `.env` before shared use.

The dashboard is intentionally operational: PostgreSQL health and row counts. Kafka metrics are not claimed because no metrics exporter is included. Grafana does not own or modify database schema.
