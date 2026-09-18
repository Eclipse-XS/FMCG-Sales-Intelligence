# Reproducibility and platform hardening V1.1

## Gate summary

The starting point was clean `main` at `d0e8284fcd39c1960d059f0a86a088e437ecf0b6`; `origin` contained no branch refs, so there was no remote divergence to reconcile. DVC was locally current but had no remote.

The tracked `gdrive` remote is now configured and `dvc-gdrive==3.0.1` is pinned. Seven processed dataset pointers and seven canonical stage outputs were audited; serving bundles are owned. `dvc push -v` reached Google OAuth and stopped at interactive consent. No token or secret entered Git. Consequently DVC push, second-push completeness, Git push and genuine remote clean-clone pull/serving parity are not claimed.

A separate local clone with a new Python 3.13.5 virtual environment completed the locked requirements install, editable package install and package import (`1.0.0`). API liveness returned 200 and readiness correctly returned 503 without DVC artifacts. A fresh `npm ci`, 7 frontend tests and production build passed. The clean clone exposed cross-platform DVC dependency hash drift from line-ending conversion; `.gitattributes` now fixes pipeline text dependencies to LF, and a second new clone confirms only the expected missing DVC-managed datasets/artifacts remain. This is `LOCAL_CLONE_REPRO_PROVEN_ONLY`, not remote artifact reproduction.

Dashboard V1.1 implements typed backend-driven global filters, URL persistence, supported-page propagation, explicit non-applicability, no-data/loading/error states, freshness/model metadata, modular ECharts and code splitting. The largest V1.1 chunk is 360.59 kB versus the former 1,341.16 kB entry bundle.

The local-demo API now has restricted CORS, body/batch/page/list limits, structured safe errors, request IDs, security headers and parameterized analytical queries. Authentication, authorization, TLS, distributed rate limits and secrets management remain production-deferred.

Kafka runtime was attempted and blocked by an unavailable Docker Desktop Linux engine. Airflow source parses, its task structure is covered, and its project root is portable; no Airflow runtime is installed. Airbyte and BigQuery remain templates.

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

## Remaining external boundary

Run `dvc push` after owner OAuth consent, verify a second no-op push, then publish Git normally and execute the documented GitHub clean-clone/DVC-pull parity proof. Until then the correct overall status is `REPRODUCIBILITY_HARDENING_V1_1_COMPLETE_WITH_EXTERNAL_AUTH_BLOCKER`.
