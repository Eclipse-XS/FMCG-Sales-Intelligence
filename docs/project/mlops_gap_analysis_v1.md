# MLOps Gap Analysis V1

| Capability | State | Evidence / gap |
|---|---|---|
| Dataset versioning | IMPLEMENTED_AND_EXECUTED | seven processed datasets have DVC pointers |
| Canonical analytical stages | IMPLEMENTED_AND_EXECUTED | seven independent DVC stages and persisted artifacts |
| Artifact manifests/metrics | IMPLEMENTED_AND_EXECUTED | manifests, metrics, reports and selected model/method contracts |
| Model serialization | IMPLEMENTED_AND_EXECUTED | joblib for Forecasting, Stockout, Survival, Segmentation and Anomaly |
| Experiment tracking | PARTIALLY_IMPLEMENTED | file-based artifacts; no queryable experiment service |
| Model registry semantics | PARTIALLY_IMPLEMENTED | canonical folders and manifests; no promotion/approval lifecycle service |
| DVC remote | MISSING | local cache only; clone cannot retrieve DVC-owned data/artifacts |
| Prediction schemas | PARTIALLY_IMPLEMENTED | training feature contracts exist; serving request/response contracts do not |
| Inference validation | MISSING | no deployed model-loader or request validation boundary |
| Monitoring/drift | PLANNED | diagnostics exist offline; no production telemetry or alerting |
| Scheduled retraining | NOT_REQUIRED_YET | insufficient real/matured evidence for arbitrary schedules |
| Rollback | MISSING | no deployed release/version rollback process |
| Serving | MISSING | no inference API or batch-serving job |
| Airflow | TEMPLATE_ONLY | DAG definition exists; no deployment/run history |
| Kafka | PARTIALLY_IMPLEMENTED | replay components and Compose profile; no durable execution report |
| Airbyte/BigQuery | TEMPLATE_ONLY | configuration exists; no runtime credentials or execution |
| Grafana | TEMPLATE_ONLY | Compose/provisioning exists; no verified model monitoring deployment |

No DVC remote prevents cross-machine retrieval of processed datasets and canonical artifacts. Git still carries source, configuration, `.dvc` pointers and compact metrics, so the dependency graph is inspectable, but a fresh clone cannot reproduce the project without reconstructing data locally. Before a portfolio/demo handoff, choose an object-store remote, document credential injection, push required DVC objects and verify a clean-machine pull.

Major next-phase gaps are: safe Git checkpointing; portable manifests; DVC remote; batch inference contracts for Forecasting and Stockout Classification; BI mart contracts; monitoring and label-maturity logic; and an end-to-end clean-machine reproduction test.
