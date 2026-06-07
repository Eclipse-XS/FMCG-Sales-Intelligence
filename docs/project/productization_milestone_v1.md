# Productization milestone V1

Status: `PRODUCTIZATION_V1_COMPLETE_WITH_BLOCKERS`.

The repository now has a generic product boundary, eleven versioned canonical data contracts, reusable company/domain packs, frozen-model inference, a typed FastAPI backend, an API-driven React dashboard, local MLflow tracking/registry, Prometheus/Grafana observability, Docker Compose profiles and fixture-safe CI. The existing seven scientific cores and their canonical metrics were not retrained or changed.

## Validated outcomes

- Python: 121 pytest tests pass; Ruff passes.
- Data quality: dbt build passes 55/55 and Great Expectations validates all eight published datasets.
- Frontend: 2 tests pass, production build passes and npm reports zero vulnerabilities.
- Docker: PostgreSQL, API, frontend, MLflow, Prometheus and Grafana passed local health/readiness checks.
- MLflow: seven canonical runs were imported without training. Forecasting and stockout classification are registered under `fsi.forecasting` and `fsi.stockout_classification`, each with alias `serving-v1`. Re-running the importer created no duplicate runs.
- Serving: live Docker requests returned a 7-day forecast and a stockout score from the canonical joblib bundles.

## Frozen scientific evidence

Forecast WAPE remains 0.3778884755; stockout average precision 0.2551216857; survival C-index 0.7922890233; segmentation remains k=3 with silhouette 0.3307169762; anomaly candidate rate remains 0.0241503797; basket output remains 1,262 rules; promotion descriptive lift remains 0.0621638304. Segment assignment remains blocked.

## Blockers and limitations

- No DVC remote exists, so clean-machine binary-artifact reproduction is not proven.
- Segment assignment is scientifically blocked and is not presented as a trained capability.
- The stack is a local product demo, not an enterprise production deployment. Authentication, authorization, TLS, rate limiting and managed secrets are absent.
- Dashboard views are API-driven and useful for the supported data, but global cross-page dimension filters are not implemented. The ECharts bundle also triggers a non-fatal chunk-size warning.
- Kafka was retained but not revalidated in this milestone. Airflow is a definition, while Airbyte and BigQuery remain templates.

## Authoritative references

- Technology state: `artifacts/project/technology_registry_v1.json`
- Machine status: `artifacts/project/productization_v1.json`
- Contracts: `contracts/registry_v1.yaml`
- Architecture: `docs/architecture/system_architecture.md`
- MLflow/DVC ownership: `docs/mlops/mlflow_v1.md`
- Serving: `docs/deployment/serving_v1.md`
- Dashboard: `docs/visualization/dashboard_v1.md`
