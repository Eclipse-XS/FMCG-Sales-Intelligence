# Optional infrastructure and reproducibility

The authoritative supported small-demo commands and API examples are in the root
README. `docker-compose.demo.yml` is independent of `.env`, PostgreSQL, MLflow,
DVC, Kafka and frozen FMCG artifacts. Main Compose is an optional local FMCG stack.

## Component purposes

- PostgreSQL: operational integrity, replay ledger and analytical publication.
- DuckDB/dbt: historical dimensional marts, processed features and read-only BI.
- MLflow: existing experiment evidence plus optional native Pipeline registry.
- DVC: versioned larger scientific datasets/artifacts; no private remote needed
  for the standalone engine demo.
- Grafana/Prometheus: optional dashboards and HTTP/model telemetry. Grafana needs
  explicit administrator credentials; anonymous access is disabled.
- Kafka: existing optional `sales.events` to PostgreSQL replay experiment. Event
  schemas, IDs and ledger are retained; this is not a supported streaming model
  inference pipeline. The consumer's database-error rollback/DLQ transaction and
  recovery behavior needs further work before dependable use. It is not part of
  the REST critical path and is excluded from the supported standalone demo.
- Airflow: existing DAG source only, not an active Compose orchestration service.

## Historical DVC lock

The scientific lock records historical outputs. The audit detected source/lock
staleness already present in the baseline. Missing shared source dependencies are
now explicit in dvc.yaml; this correctly invalidates those stages for a future
reproduction. We do not falsely stamp existing output metrics as regenerated
under changed dependency declarations. `dvc status` may report stale stages and
missing local cache until inputs/cache are provisioned and `dvc repro` is run.
The canonical artifacts and published numerical results are preserved.
The local regression audit uses a copy of existing frozen inputs; it is not
proof of fresh scientific retraining or of private remote availability.

Historical deployment documents describe the earlier academic platform. Prefer
the root README for currently verified engine installation/startup. The larger
warehouse/scientific toolchain still uses requirements.txt and requires its own
inputs; the smaller install uses pyproject.toml extras.
