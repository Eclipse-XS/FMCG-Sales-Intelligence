# MLflow V1

MLflow 3.16.1 runs in the optional `mlops` Compose profile. It uses a distinct PostgreSQL `mlflow` database and persistent `mlflow_artifacts` volume. Stable experiments are `fmcg-sales-intelligence/<task>` for all seven implemented cores. Forecasting and Stockout Classification receive registry names `fsi.forecasting` and `fsi.stockout_classification` with honest `serving-v1` aliases; analytical tasks receive runs but no fake models.

`CanonicalMLflowImporter` reads existing manifests/metrics and logs `training_executed=false`. Identity is task + V1 + trusted artifact SHA-256, making import idempotent. It does not recompute metrics. DVC remains authoritative for datasets, pipelines and canonical artifacts; MLflow owns run/registry metadata and copies selected evidence for browsing.

MLflow is isolated because its runtime dependency graph is independent from the frozen pandas/PyArrow environment. Run it through Docker or a separate environment using `requirements-mlflow.txt`. API readiness does not depend on MLflow availability.

## DVC and MLflow ownership

| Artifact / metadata | Git | DVC | MLflow | Why |
|---|---:|---:|---:|---|
| source code and configuration | yes | no | no | reviewable repository history |
| raw and generated datasets | pointer only | yes | no | reproducible large-file lineage |
| canonical model binaries | pointer/manifest | yes | copy for eligible registry entries | DVC remains the binary source of truth |
| metrics and scientific manifests | yes where small | yes with canonical directory | browsable copy | immutable evidence plus run discovery |
| experiment/run metadata | no | no | yes | searchable experiment history |
| model registry metadata and aliases | no | no | yes | deployment-facing catalog semantics |
| dashboard build artifact | source only | no | no | rebuilt through npm/Docker |

The canonical importer never calls training. It identifies each import using the canonical model or manifest SHA-256. The verified local import contains seven runs and two registered models. A second import created no additional runs.
