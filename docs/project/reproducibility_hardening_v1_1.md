# Reproducibility and platform hardening V1.1

## Gate summary

The milestone is now `PROVEN_FROM_GITHUB_AND_DVC`. The repository was published to GitHub with normal, non-forced pushes and reproduced in an independent clone from the GitHub URL.

The tracked `gdrive` remote is configured and complete. Initial and no-op pushes passed. A clean-clone pull exposed and resolved ownership gaps for processed contracts, segment-assignment features, generated validation inputs, metrics, and the analytical warehouse. OAuth client material remains only in ignored local DVC configuration; no credential or token entered Git.

A fresh Python 3.13.5 virtual environment installed the dependency set and package 1.0.0. DVC restored the required data and artifacts; API liveness and readiness both returned 200. Forecasting and stockout serving matched the original checkout exactly. Offline analytics read the restored outputs and warehouse. The reproduction status is `PROVEN_FROM_GITHUB_AND_DVC`.

Dashboard V1.1 implements typed backend-driven global filters, URL persistence, supported-page propagation, explicit non-applicability, no-data/loading/error states, freshness/model metadata, modular ECharts and code splitting. The largest V1.1 chunk is 360.59 kB versus the former 1,341.16 kB entry bundle.

The local-demo API now has restricted CORS, body/batch/page/list limits, structured safe errors, request IDs, security headers and parameterized analytical queries. Authentication, authorization, TLS, distributed rate limits and secrets management remain production-deferred.

Docker Desktop was started safely but its Linux engine remained unavailable after the bounded poll. Current Compose, MLflow, Kafka, and Airflow-container checks therefore remain optional runtime blockers. Airflow source and task structure remain covered; Airbyte and BigQuery remain templates.

## Validation

- pytest: 124 passed, 3 skipped; warnings are dependency deprecations.
- dbt: 55/55 PASS.
- Great Expectations: 8/8 published datasets PASS.
- frontend: 7/7 tests PASS; build PASS; npm audit 0 vulnerabilities; no chunk over 500 kB.
- focused Ruff scope: PASS. Full-repository Ruff remains a pre-existing formatting backlog and was not mass-reformatted.
- DVC: local status current; gdrive default visible; doctor confirms gdrive support.
- dependency check: no broken requirements.
- secret/large-file gate: no tracked `.env`, OAuth credential, private key, or tracked file over 1 MB.
- Docker: current revalidation `BLOCKED_ENVIRONMENT`; prior V1 evidence is not relabeled as current proof.

## Scientific invariants

No training or final evaluation was run. Persisted metrics remain: Forecast WAPE `0.3778884755`; Stockout AP `0.2551216857`; Survival C-index `0.7922890233`; segmentation `k=3`, silhouette `0.3307169762`; anomaly rate `0.0241503797`; basket rules `1262`; promotion descriptive units change `0.0621638304`; Segment Assignment `BLOCKED / NOT_READY`.

## Remaining optional runtime boundary

Cross-machine GitHub+DVC reproduction is proven. The only current environment limitation is the unavailable Docker Linux engine, which prevents re-executing the optional container runtime checks in this milestone.
