# Runtime platform validation V1.2

| Component | Version | Executed evidence | State |
|---|---|---|---|
| Docker Engine | 29.7.2, Linux x86_64 | Docker Desktop launched normally; `docker info` succeeded | ACTIVE_EXECUTED_LOCAL |
| Compose | 5.5.1 | Existing core, mlops, observability and streaming profiles started; declared health checks passed | ACTIVE_EXECUTED_LOCAL |
| PostgreSQL | 17 | Healthy; `fmcg` accessible with 35,032 sales rows | ACTIVE_EXECUTED_LOCAL |
| FastAPI | package 1.0.0 | `/health`, `/ready`, `/version`, contracts, capabilities, models, analytics and membership assignment returned success; API restart restored readiness | ACTIVE_EXECUTED_LOCAL |
| MLflow | 3.16.1 | 7 experiments/7 canonical runs; two syncs created zero duplicates; aliases `serving-v1` persisted after restart | ACTIVE_EXECUTED_LOCAL |
| Prometheus | 3.5.0 | readiness 200; `fsi-api` target `up`; request, latency and inference metrics present after bounded traffic | ACTIVE_EXECUTED_LOCAL |
| Grafana | 11.5.2 | health 200; datasource and dashboard provisioning completed | ACTIVE_EXECUTED_LOCAL |
| Kafka | 3.9.0 | broker healthy; deterministic valid replay consumed; second replay left ledger/replay at 20 rows; invalid events reached DLQ | ACTIVE_EXECUTED_LOCAL_SIMULATION |
| Airflow | 2.10.5 | ephemeral local container discovered DAGs and executed `fmcg_runtime_smoke.verify_frozen_evidence` successfully | ACTIVE_EXECUTED_LOCAL_ORCHESTRATION_DEMO |

Kafka remains an isolated replay simulation, not production streaming. Airflow runtime was an ephemeral local validation, not a persistent deployment. MLflow owns metadata while DVC remains authoritative for data, pipelines, and canonical artifacts.
