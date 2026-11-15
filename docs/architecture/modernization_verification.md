# Modernization verification — 2026-11-16

## Scope and implementation phases

| Phase | Implemented result | Gate |
|---|---|---|
| 1 Reliability | Artifact-independent fixtures/CI, deterministic demo, structured availability errors, secured Grafana/default credentials, repeatable database indexes | Verified |
| 2 Decoupling | engine contracts/data/runtime separated from product/science; existing canonical forecasting/classification bridged | Verified |
| 3 Model extensibility | MLflow native signatures and versioned sklearn Pipeline registration; explicit immutable deployment approvals | Verified |
| 4 Integration | Shared Engine import API and resource-oriented REST; actual HTTP byte/batch bounds; legacy wrappers retained | Verified |
| 5 Independent domain | Deterministic churn Pipeline, typed mapping/domain YAML, CSV/Parquet and REST/Python parity | Verified |
| 6 Operations | Request IDs, sanitized errors, bounded metric labels, optional one-service Docker, PostgreSQL integration, replay-only Kafka separation | Verified |
| 7 Final audit | 171 full-regression tests plus 2 subsequently added tests passed; implementation CI green | Verified; merge remains gated on final documentation commit CI |

## Verification history

- Baseline original local checkout: 29 unit tests passed because pre-existing
  artifacts were present. GitHub baseline run 36105896055: 14 failed, 15 passed.
- First new isolated run: 34 passed; first engine integration run: 5 passed.
- Isolated suite after declarative-domain test: 40 passed. Two credential/timeout
  unit tests were subsequently added and passed separately.
- Canonical assertions after local fixture provisioning: 11 passed; additional
  real-model engine parity test: 1 passed.
- First broad historical regression: 121 passed, 9 failed. Four failures were
  incomplete local CSV copying, two were missing tabulate, two were missing raw
  warehouse/demand fixtures, and one was an empty database after loader rollback.
  Assertions were retained. Fixtures were completed, tabulate declared in
  analytics requirements, and duplicate index creation fixed.
- Targeted repaired EDA/promotion/refinement: 10 passed.
- An early database run against the rolled-back import: 1 failed, 2 passed.
  Re-import after idempotent indexes succeeded for all 18 operational tables;
  database tests then passed 3/3 in 1.49 seconds. Two intermediate local runs
  stalled and were stopped; explicit connection timeouts and IPv4 local example
  configuration were added. Stopped runs are not counted as passes.
- Local Docker demo: image built from pyproject dependencies, non-root API became
  healthy; real HTTP churn and demand requests succeeded with version metadata.
  Example churn prediction: 1; synthetic demand prediction: approximately 32.48.
  These are smoke outputs, not model quality metrics.
- 134 existing canonical files compared byte-for-byte with original local
  artifacts: all SHA-256 hashes identical. No scientific retraining claimed.
- Scientific source and config/modeling diff against d37585e: empty.
- Ruff checks passed throughout after removing unused imports.
- GitHub push/PR runs 43776486184 and 43776491119 at e5e9d75: all lint, isolated and
  docker-demo jobs succeeded. Later commits require their own green checks.

## Final verification results

- Full provisioned local suite: **171 passed, 0 failed, 0 skipped**, 217.90 s.
  Collection preceded the two new credential/timeout tests; those passed **2/2**
  separately and are included in final CI. All 173 currently collected tests
  therefore have passing evidence; no combined 173-test run is claimed.
- Final implementation commit `3048a15`: GitHub runs **43777041007** and
  **43777045243**, all lint/isolated/docker-demo jobs successful.
- PostgreSQL: **3 passed**, 1.49 s, after successful import of all 18 tables.
- Canonical parity: exact predictions for both real forecasting/classification
  bundles; all 134 canonical artifacts retain identical hashes.
- `ruff check .`: **PASS**. CLI demo with native local MLflow registry: **PASS**.
- Machine-readable summary: `modernization_evidence.json`. Local JUnit files
  remain under `artifacts/modernization-*.xml` and are intentionally ignored.
- Delivery: [PR #2](https://github.com/Eclipse-XS/FMCG-Sales-Intelligence/pull/2).
  This report is recorded before merge. GitHub's PR merge event is the delivery
  authority; the final response records the merge SHA. Merge is permitted only
  after this documentation commit has green checks.

## Acceptance criteria

| Criterion | Evidence / scope | Status |
|---|---|---|
| AC-01 Core independence | AST/import/business-term checks; engine imports no product/science/integration modules | PASS |
| AC-02 Domain extensibility | Customer retention registered by integration code and declarative YAML without core edits | PASS |
| AC-03 BYOM | Real SQLite MLflow registration of fitted Pipeline versions 1/2, signatures and reload; explicit version selection | PASS |
| AC-04 Data compatibility | Missing/extra/per-row fields, forbidden outcomes, nulls, category/type/finite values, mapping collisions and post-transform checks | PASS |
| AC-05 Inference | Shared Python/REST results and real container HTTP requests; canonical bridge parity | PASS |
| AC-06 Scientific preservation | Seven unchanged scientific implementations/configurations and 134 unchanged canonical file hashes | PASS |
| AC-07 Reproducibility | CI clean checkout installs and runs synthetic demo; Docker has no private/DVC/DB inputs | PASS |
| AC-08 CI reliability | Independent lint/isolated/container jobs all passed for implementation; final docs commit checked before merge | PASS (merge gate enforced) |
| AC-09 Security | Explicit secrets, no anonymous Grafana, loopback ports, operator artifact trust; no upload/deserialization HTTP surface | PASS |
| AC-10 Kafka scope | Optional experimental ingestion replay explicitly excluded from inference demo | PASS |
| AC-11 Documentation | Startup/API/model/domain examples exercised by tests, demo and Docker smoke | PASS |
| AC-12 Engineering quality | Modular application, shared engine/service, existing libraries, no extra persistent registry or speculative microservices | PASS |
| AC-13 Git delivery | Dedicated branch, real-time commits, pushed PR #2; merge event/HEAD SHA recorded in delivery response | PENDING until PR merge event |

## Changed modules

- `engine/{contracts,data,runtime}.py`: typed signatures, source normalization,
  injected domain/model registries, task execution and output checks.
- `integrations/{api,mlflow,trust,approve,fmcg,demo}.py`: shared HTTP routes,
  MLflow operator registration/loading, local approval boundary, compatibility
  bridge and independent synthetic examples.
- `product/api/app.py`, `product/adapters.py`, `product/serving/*`: generic routes,
  structured errors/telemetry/body limits, DataFrame reader, per-row feature
  checking and approved canonical loading. Existing scientific execution stays
  in the original modules.
- `pipelines/persistence/connection.py`, analytical publisher, PostgreSQL index
  DDL: explicit/escaped credentials, bounded connections and repeatable indexes.
- `config/frozen_models.yaml`, customer-retention domain YAML: deployment-specific
  configuration kept outside reusable core.
- `tests/conftest.py`, `tests/unit`, `tests/engine`, `tests/canonical`, one existing
  integration AST guard: local fitted fixtures, behavioral negatives, API/
  MLflow parity, retained canonical assertions and real canonical parity.
- README, modernization audit/comparison/deployment docs, pyproject/requirements,
  CI, Compose files, ignore rules and DVC dependency declarations.

## Remaining limitations and production assessment

The supported deliverable is a verified local integration engine. It lacks API
authentication/tenant isolation, HA, load/capacity evidence, model sandboxing,
resource isolation for operator Python transforms and a production SLA. Use a
trusted deployment boundary and external authentication before external exposure.
MLflow uses one process-global URI and caches load outcomes; restart to retry an
unavailable model. Models, registry writers and artifact storage must be trusted.
MemoryRegistry is intentionally nonpersistent and explicit versions are required
when ambiguous. Full online feature computation/time joins remain domain work.

The historical DVC lock already had source drift; new shared dependencies now
correctly invalidate the stages. The lock was not dishonestly refreshed against
unretrained historical outputs. Larger scientific reproduction still needs its
separate data/provenance/cache setup. The fresh-clone demonstration itself has
no private dependency. Frozen metric values were not changed or revalidated as
production outcomes.

Kafka replay remains experimental with transaction/DLQ/recovery limitations;
no streaming inference guarantee is made. Airflow is retained DAG source, not a
started orchestrator. Optional full monitoring/MLflow infrastructure was not
end-to-end capacity tested. Local Python packages emitted upstream deprecation
warnings; no assertions were weakened or failing tests skipped for a green badge.
