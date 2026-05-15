# FMCG Sales Intelligence

Operational PostgreSQL foundation for a synthetic beverage company. The hierarchy is `category → brand → product → SKU`; the SKU is the sellable and stocked unit. No generated record is represented as internal Coca-Cola company data.

## Reproduce

```powershell
Copy-Item .env.example .env
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python src/ingestion/download_sources.py
.venv\Scripts\python src/profiling/profile_sources.py
.venv\Scripts\python src/generation/generate_dev_data.py
.venv\Scripts\python src/validation/validate_generated.py
docker compose up -d
```

Competition downloads remain unavailable, so reproducible mirror provenance is explicit: Favorita uses `evgeniypolin/favorita-grocery-sales-forecasting`; M5 uses University of Nicosia Zenodo record `10.5281/zenodo.10203108`; Instacart uses the CC0-declared `psparks` mirror. Canonical filenames, columns and M5 MD5 checksums are verified before use. Keep credentials outside the repository. Raw files are immutable inputs and ignored by Git.

## Architecture

`data/raw` preserves downloads. Profiling records evidence in `data/metadata`; unrelated IDs are never joined. Donors inform distributions used by deterministic generation. PostgreSQL holds operational facts only. Analytical features and model outputs remain outside the operational schema.

The development generator is intentionally small by default. It creates correlated store/SKU/day demand, seasonal and weekend effects, promotion response, constrained sales, inventory depletion and lead-time-like replenishment. It does not claim to reproduce donor distributions until all donor profiles are available.

## Operational PostgreSQL Database

Prerequisites: Docker Desktop with Linux containers and Python 3.11+ with the packages in `requirements.txt`. The project maps PostgreSQL to host port `55432` by default because port 5432 is commonly occupied by a native installation.

Create the local configuration and Python environment:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

Generate canonical data, start PostgreSQL, recreate the schema, load data and validate it:

```powershell
.venv\Scripts\python src/generation/generate_dev_data.py --days 90 --stores 20 --skus 48
docker compose up -d
.venv\Scripts\python src/database/create_schema.py --reset
.venv\Scripts\python src/database/load_data.py
.venv\Scripts\python src/database/validate_database.py
.venv\Scripts\python -m pytest -q
```

`create_schema.py --reset` drops only the `fmcg` schema and is the supported local-development reset. The loader uses one transaction, dependency-safe ordering and PostgreSQL `COPY`; any error rolls back the entire load. It loads only canonical files from `data/generated`, never raw donors. Validation writes `reports/database_validation.md` and its machine-readable JSON equivalent.

Connect with `psql`:

```powershell
$env:PGPASSWORD = 'change_me'
psql -h localhost -p 55432 -U fmcg -d fmcg
```

Use the same host, port, database, user and password in DBeaver or pgAdmin. Configuration comes from `.env`; do not commit that file. Operational smoke queries are in `db/queries/smoke.sql`.

To destroy the local project database completely and recreate it:

```powershell
docker compose down -v
docker compose up -d
.venv\Scripts\python src/database/create_schema.py --reset
.venv\Scripts\python src/database/load_data.py
.venv\Scripts\python src/database/validate_database.py
```

The `-v` command deletes only this Compose project's PostgreSQL volume. Derived ML features and predictions are deliberately excluded from the operational schema.

## Data platform

The operational schema remains the source of record. The executed analytical fallback is DuckDB: `src/warehouse/extract_operational.py` copies all 18 `fmcg` tables to `data/warehouse/fmcg.duckdb` under the `raw` schema and writes matching raw Parquet extracts. This includes the complete `daily_demand` date × store × SKU grid that distinguishes requested, realized and inventory-censored demand. dbt builds `analytics` staging, intermediate, dimensions, facts and marts in the same DuckDB database. Polars then creates versioned Parquet datasets; Great Expectations checks their contracts.

Run the complete local analytical path after the OLTP database is loaded:

```powershell
.venv\Scripts\python src/pipeline/run_local.py
.venv\Scripts\python -m pytest -q
```

The generated datasets are `forecasting`, `stockout`, `segmentation`, `segment_assignment`, `anomaly`, `basket`, and `promotion_performance`. Forecasting scores at the start of day `t`; its model features contain no realized values from `t`, and its target is the fully observed sum over `(t,t+7]`. Anomaly detection is explicitly post-event. `segment_assignment` is only a compatibility alias of the pre-clustering segmentation features and contains no cluster label or target. The artifacts are ignored by Git. Dataset contracts, point-in-time rules and feature definitions are in [docs/data/dataset_contracts.md](docs/data/dataset_contracts.md) and [docs/data/feature_catalog.md](docs/data/feature_catalog.md). Lineage is in [docs/data/lineage.md](docs/data/lineage.md).

DuckDB is executed and validated locally. BigQuery is a configured target template only; no BigQuery load is claimed without credentials. Airbyte is likewise a deployment template only; the local extractor provides the executed bounded batch replication path. Details: [BigQuery](docs/operations/bigquery.md), [Airbyte](docs/operations/airbyte.md).

## Streaming and operations

Kafka is an optional Compose profile. It is isolated from the operational `fmcg` schema and demonstrates a schema-validated sales replay, DLQ and idempotent consumer materialization:

```powershell
docker compose --profile streaming up -d
.venv\Scripts\python src/streaming/init_streaming.py
.venv\Scripts\python src/streaming/produce_replay.py
.venv\Scripts\python src/streaming/consume_replay.py
```

Kafka UI is available at `http://localhost:8088`. The producer uses broker-level idempotence; replay rows are deduplicated by `event_id`. One deliberately malformed event exercises `sales.dlq`. See [Kafka operations](docs/operations/kafka.md).

`dags/fmcg_platform.py` supplies an Airflow DAG definition but Airflow is not deployed in this environment, so no DAG execution is claimed. Start the optional Grafana profile with `docker compose --profile observability up -d`; its provisioned operational dashboard is at `http://localhost:3001`. See [Airflow](docs/operations/airflow.md) and [Grafana](docs/operations/grafana.md).

## Modeling and reproducibility status

Forecasting Modeling V1, Stockout Classification V1, Stockout Survival V1, Store Segmentation V1 and Sales Anomaly Detection V1 are implemented and verified. Store segmentation outputs versioned pseudo-labels, not ground truth. Anomaly V1 compares a strict-prior rolling z-score with reference-fitted Isolation Forest and produces unreviewed candidates rather than verified anomaly labels. Segment Assignment, the remaining ML tasks, a production API, MLflow and production deployment are not implemented.

DVC locally owns the ML-ready forecasting Parquet and the canonical Forecasting V1 model, predictions and metrics. The repository currently has no DVC remote. On this machine, Git metadata plus the local DVC cache can reproduce the current artifact state. On another machine, a Git clone provides code and DVC metadata only; `dvc pull` cannot recover binary artifacts until a project-approved remote is configured and populated. A future setup would use `dvc remote add -d <name> <remote>` followed by `dvc push`, then `dvc pull` after cloning elsewhere. No provider or credentials are selected by this repository.
