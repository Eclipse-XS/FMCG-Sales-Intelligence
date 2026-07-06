# Clean-clone reproduction V1

Status: `PROVEN_FROM_GITHUB_AND_DVC`.

An independent directory was cloned from the actual GitHub repository. It did not inherit the original virtual environment, DVC cache, datasets, artifacts, MLflow state, frontend dependencies, or Docker volumes. A new Python 3.13.5 environment installed the repository dependencies and package version 1.0.0.

The tracked Google Drive remote plus local-only OAuth configuration restored the processed contracts, generated validation inputs, analytical warehouse, canonical model bundles, metrics, and offline analytical outputs. `dvc status` reported that data and pipelines were up to date. Credential material remained in ignored local DVC configuration and was not copied into Git.

FastAPI health and readiness returned 200. Forecasting and stockout inference matched the original checkout exactly for the persisted smoke inputs. Forecast semantics remain `target_units_next_7d` over `(t,t+7d]`; stockout used the frozen threshold `0.7695666515458811`. Offline analytics read restored canonical outputs without recomputation.

Validation completed with pytest 124 passed and 3 skipped, Ruff PASS, dbt 55/55 PASS, Great Expectations 8/8 PASS, frontend 7/7 PASS, npm audit with zero vulnerabilities, and production build PASS. The largest frontend chunk remained 360.59 kB.

Docker Desktop was installed but its Linux engine did not become available during the bounded safe startup attempt. Therefore current MLflow, Compose, Kafka, and Airflow-container runtime checks remain optional environment blockers; prior evidence is not relabeled as a current execution.

No model was retrained and no final scientific evaluation was recomputed.
