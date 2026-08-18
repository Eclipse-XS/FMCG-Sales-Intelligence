# Modernization baseline (2026-11-16)

Base: d37585e. Work is isolated from the original dirty main worktree.

## Confirmed defects
- GitHub run 36105896055: 14 failed, 15 passed. Missing generated CSV,
  processed Parquet and canonical artifacts; business routes returned 500/503.
- Local original worktree: 29 unit tests pass with pre-existing private/local
  artifacts. This does not establish fresh-clone reproducibility.
- FrozenModelRegistry.SPECS fixes two model names and unconditionally joblib-loads
  local bundles. No explicit artifact trust approval or general signature.
- FileAdapter supports only CSV/Parquet renaming; no dtype/null/category contract.
- API RuntimeError escapes as 500; body limit trusts Content-Length; telemetry
  uses unbounded raw URL labels. Readiness covers only fixed canonical bundles.
- Grafana permits anonymous Admin; default passwords are change_me.
- README canonical demand/stockout/survival paths are wrong; Makefile references
  have no implementation. CI lint is blocked by failed tests.

## Existing boundaries and execution paths
- science.cli -> science.run_experiment -> forecasting, stockout, survival,
  segmentation, anomaly, basket, promotion experiment modules. Keep all seven,
  config/modeling contracts, embargo/splits, evaluation and manifests intact.
- product/api -> serving (registry, inference, feature resolver, segmentation);
  analytics read/BI/publication services remain domain-specific.
- product/contracts registry_v1 and product/domains YAML profiles are useful
  FMCG contracts, not universal feature schemas. Keep these interfaces.
- pipelines generation/refinement/datasets/validation -> PostgreSQL operational
  persistence -> DuckDB/dbt marts. Preserve SQL publication/reporting paths.
- dvc.yaml has seven canonical scientific stages. Dataset inputs are separately
  DVC-tracked; private gdrive is the default remote. A separate tiny demo must
  not overwrite these scientific outputs or claim their metrics.
- tracking/CanonicalMLflowImporter publishes metrics and raw joblib directories;
  these are not MLflow pyfunc models with model signatures. Add a distinct
  signed sklearn registration path using MLflow itself for persistent registry.
- Kafka replay consumer writes sales to PostgreSQL with stable event IDs and
  DLQ; it performs no inference. Keep explicitly experimental and optional,
  outside supported synchronous demo. No claim of reliable streaming inference.
- Compose profiles: core API/publisher, streaming Kafka/UI, mlops MLflow,
  observability Grafana/Prometheus/API; full-demo omits Grafana. PostgreSQL has
  no profile; API image omits psycopg despite BI imports. Airflow is not a
  running Compose service; do not promise scheduled orchestration.
- tests/unit mixes isolated checks and canonical-data integration assertions.
  tests/scientific, tests/runtime and most tests/integration require substantial
  frozen data, database or artifacts. Move artifact assertions to an explicitly
  runnable canonical suite; retain assertions, create isolated business tests.

## Priorities, migration and risks
1. Isolate tests, fix error/security defaults, independently run lint.
2. Add small engine package with no domain imports, strict signatures, source
   normalization, runtime protocols and injected model/domain registries.
3. MLflow native signatures/versions for trusted deployments; in-memory registry
   for deterministic sklearn demos. No HTTP artifact upload or dynamic imports.
4. Shared Python/API service; bridge existing frozen forecasting/classification
   execution without retraining or modifying their scientific algorithms.
5. Deterministic churn Pipeline and FMCG fixture demos with no DVC dependency.
6. Test clean install, REST/SDK parity, legacy parity, unavailable models/errors.

Risks: serialized Python models execute code, even when MLflow loads them.
Only operators may approve immutable local hashes/trusted MLflow URIs. A hash
is integrity evidence, not a sandbox or proof of safe provenance. Large canonical
experiments remain separately reproducible; never replace their evidence with
small synthetic demo metrics. Docker/database/DVC checks depend on available
services and must be reported separately from code-level validation.
