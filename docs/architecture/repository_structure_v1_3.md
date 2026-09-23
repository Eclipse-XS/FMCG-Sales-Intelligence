# Repository structure V1.3

V1.3 establishes one explicit ownership boundary for each repository concern.

```text
apps/                         dashboard application
artifacts/
  canonical/                 DVC-owned frozen scientific outputs
  reports/                   generated analytical and validation reports
  project/                   machine-readable project evidence
config/
  contracts/                 canonical external contracts
  domains/                   replaceable domain packs
  modeling/                  scientific configuration
data/                        external, generated, processed and warehouse data
docs/                        maintained and historical documentation
platform/
  postgres/                  operational schema and bootstrap SQL
  dbt/                       analytical warehouse project
  airflow/dags/              bounded orchestration definitions
  docker/                    service images
  observability/             Prometheus and Grafana configuration
  airbyte/                   connector template
src/fmcg_sales_intelligence/
  product/                   API, serving, analytics and contracts
  science/                   seven scientific cores and EDA
    <core>/__init__.py       stable package-level API facade
    <core>/experiment.py     scientific experiment implementation
  pipelines/                 ingestion through validation and streaming
  tracking/                  MLflow canonical import integration
  common/                    genuinely shared low-level utilities
tests/                       unit, integration, scientific and runtime tests
tools/                       developer utilities
```

## Ownership rules

- Application and runtime behavior belongs to `product`; model and analytical implementation belongs to `science`.
- Data movement and construction belongs to `pipelines`; deployable tool-native assets belong to `platform`.
- Configuration data belongs to `config`; Python loaders for it remain in the package.
- Datasets belong to `data`; frozen model objects belong to `artifacts/canonical`; generated human and machine reports belong to `artifacts/reports`.
- Tests are classified by the boundary they protect, not by milestone chronology.

## Domain boundary

`config/domains/coca_cola_demo` is synthetic, unofficial presentation configuration. Generic product and scientific code does not import it. `_template` and `generic_demo` prove that company configuration remains replaceable.

## Compatibility

The pre-migration joblib audit loaded all six serialized bundles as plain dictionaries containing third-party estimators and metadata. No repository-defined module path was required, so no legacy import shim exists. Historical milestone documents retain historical statements; current operational guidance points to V1.3 paths.

## Intentional exceptions

Tool-native root files (`docker-compose.yml`, `dvc.yaml`, `dvc.lock`, `pyproject.toml`, requirements and Git/DVC metadata) remain at root. Empty local legacy directories can remain physically in an existing checkout only because ignored interpreter caches are not Git objects; clean clones do not contain them.
