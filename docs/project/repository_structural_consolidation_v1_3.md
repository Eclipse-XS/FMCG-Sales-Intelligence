# Repository Structural Consolidation V1.3

## Scope and starting point

The migration started from clean `main` at `60d9cb9688055e33b9cbaf8a52da5e71a01b72fd`. It addressed competing Python roots, scattered configuration and platform directories, a second report root, flat tests, and a processed-data dependency stored under reports.

## Physical migration

| Previous path | Current owner |
|---|---|
| `configs`, `contracts`, `domain_packs` | `config/modeling`, `config/contracts`, `config/domains` |
| `db`, `dbt`, `dags`, `infrastructure/*` | `platform/*` |
| `src/modeling`, `src/eda` | `src/fmcg_sales_intelligence/science` |
| phase-oriented `src/*` packages | `src/fmcg_sales_intelligence/pipelines` |
| product API/serving/analytics/contracts | `src/fmcg_sales_intelligence/product` |
| `reports` | `artifacts/reports` |
| `scripts` | `tools` |
| flat `tests` | `tests/unit`, `integration`, `scientific`, `runtime` |

`reports/data_refinement/stockout_episodes.parquet` was reclassified as `data/processed/stockout/stockout_episodes.parquet` and is now DVC-owned. DVC stage commands and dependencies were path-migrated and the lock was reconciled without stage execution or retraining.

## Compatibility and invariants

All six canonical joblib bundles were loaded before migration. Their top-level value is a plain dictionary and no repository module name is required for deserialization; compatibility shims were therefore rejected as unnecessary. Pre/post canonical SHA-256 values are identical. Forecast output, stockout probability and threshold have exact parity.

## Validation evidence

- pytest: 130 passed sequentially.
- Ruff: all intended source/test/tool/DAG scope passed, with only the documented inherited compact-format exclusions `E401`, `E701`, and `E702`.
- dbt: 55/55 PASS.
- Great Expectations: 8/8 datasets PASS.
- frontend: 7/7 tests, build PASS, audit 0 vulnerabilities.
- PostgreSQL: healthy, 18 operational tables, 35,032 sales rows.
- FastAPI: health, readiness, version, contracts, capabilities and models returned HTTP 200.
- Docker profiles: PostgreSQL, API, frontend, MLflow, Prometheus, Grafana, Kafka and Kafka UI healthy/running.
- Kafka: bounded replay and invalid-event DLQ behavior passed; replay remained idempotent at 20 ledger and sales rows.
- Airflow: both DAGs discovered in an ephemeral 2.10.5 runtime; `verify_frozen_evidence` passed with `training_executed=false`.
- DVC: status clean, two pushes reported everything up to date, cloud status synchronized.

## Clean-clone proof and commits

The clean-clone result and final commit identities are finalized after feature-branch validation and normal main integration. No data, model, environment, DVC cache, Docker state or credentials are copied into the reproduction workspace.

## Documented exceptions

Airflow remains a bounded local demo, not a persistent scheduler deployment. Ruff retains three pre-existing compact-style rule exclusions to avoid a non-structural mass rewrite. The minimal MLflow image can run canonical sync directly but does not expose the product CLI because its intentionally isolated dependency set omits API metrics dependencies. Ignored cache-only legacy directories may remain in this existing checkout but are absent from Git and clean clones.
