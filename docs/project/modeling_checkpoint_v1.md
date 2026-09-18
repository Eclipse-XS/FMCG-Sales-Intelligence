# Project-Wide Modeling Checkpoint V1

## Executive status

The planned V1 scope is complete: seven independent analytical/modeling cores are implemented and DVC-owned. Segment Assignment is deliberately blocked because clustering labels are not stable enough to become a supervised target. No core is production-deployed.

## Core registry

| Core | Readiness | Selected method | Primary persisted result | Execution decision |
|---|---|---|---|---|
| Forecasting | READY_WITH_LIMITATIONS | CatBoost regressor | Test WAPE 0.3779 versus 0.5259 trailing-7-day baseline | scheduled batch inference; API optional |
| Stockout classification | READY_WITH_LIMITATIONS | Histogram gradient boosting | AP 0.2551, ROC-AUC 0.7991, Brier 0.0635; 15/33 episodes detected | scheduled batch risk scoring; API optional |
| Stockout survival | READY_WITH_LIMITATIONS | L2 Cox PH | test C-index 0.7923; mean horizon Brier 0.0292 | offline experimental analysis |
| Segmentation | READY_WITH_LIMITATIONS | KMeans, k=3 | silhouette 0.3307; DBI 0.9043; retention 52.5% | offline human-review analytics |
| Segment assignment | BLOCKED | none | pseudo-label readiness NOT_READY | blocked |
| Anomaly | READY_WITH_LIMITATIONS | Isolation Forest plus z-score baseline | 2.42% IF candidate rate; Jaccard agreement 0.0173 | scheduled human-review candidate detection |
| Basket | READY_WITH_LIMITATIONS | FP-Growth, Apriori cross-check | 1,262 canonical rules; 94 stable top rules | offline BI/review |
| Promotion | READY_WITH_LIMITATIONS | matched-duration descriptive comparison | observed PRE-to-DURING aggregate difference +6.22%; sign stability 79.69% | offline BI/review |

Forecasting predicts realized units summed over `(t,t+7]`, not same-day demand. Its first final-test process reached test evaluation and then failed during downstream residual construction because Decimal outcomes and float predictions were incompatible. The canonical rerun retained the frozen model, features, parameters, split and seed. The test partition was therefore read by both the aborted technical attempt and the successful canonical run.

## Scientific freeze

- Forecasting and stockout classification are the only immediate predictive serving candidates.
- Survival remains offline because only 73 physical episodes support the analysis and the selected Cox specification has an `available_quantity` PH violation.
- Segmentation is an exploratory clustering result, not a production segmentation system.
- Anomaly outputs are candidates, never confirmed anomalies.
- Basket rules are associations, not recommendations or causal relationships.
- Promotion differences are observed matched-window differences, not causal effects.
- Segment Assignment has no model, DVC stage or production labels.

## Serving and offline decisions

| Core | New-data prediction | Fitted state | Latency | Cadence | Human review | Endpoint |
|---|---:|---:|---|---|---:|---|
| Forecasting | yes | yes, joblib | low priority | daily/weekly batch | no | batch first; endpoint optional |
| Stockout classification | yes | yes, joblib | operational | daily batch or event-triggered | alerts may be reviewed | batch first; endpoint useful |
| Stockout survival | possible, not approved | yes, joblib | no | on-demand research | yes | no |
| Segmentation | assignment technically possible, scientifically blocked | yes, joblib | no | monthly/on-demand | yes | no |
| Anomaly | scoring new observed events | yes, joblib | no | daily batch | required | no immediate endpoint |
| Basket | no fitted predictor | no | no | monthly/on-demand | required | no |
| Promotion | no fitted predictor | no | no | after campaign windows mature | required | no |

## BI consumption

- Forecasting: forecast, actual after maturity, WAPE, bias and forecast horizon.
- Stockout: risk score, risk band, threshold, event maturity and episode diagnostics.
- Segmentation: reviewed cluster profiles only; do not publish pseudo-label assignment as authoritative.
- Anomaly: score, method flags, context and `UNREVIEWED` status.
- Basket: reviewed support, confidence and lift with temporal stability.
- Promotion: eligible PRE/DURING/POST units/day, revenue/day, price and inventory context.
- Survival: research diagnostics only until PH and event-count limitations are addressed.

## Dataset ownership

| Dataset | Rows | Grain/date range | DVC | Consumers |
|---|---:|---|---:|---|
| forecasting | 86,400 | date × store × SKU; 2024-01-01–03-30 | yes | Forecasting |
| stockout | 17,280 | date × warehouse × SKU; 2024-01-01–03-30 | yes | Classification, Survival |
| segmentation | 60 | snapshot × store; 2024-01-31–03-30 | yes | Segmentation |
| segment_assignment | 60 | alias of segmentation feature contract | no | none; blocked artifact |
| anomaly | 35,032 | positive event date × store × SKU | yes | Anomaly |
| basket | 24,370 | order × SKU | yes | Basket |
| promotion_daily | 259,200 | promotion × store × SKU × calendar date | yes | Promotion |
| promotion_performance | 2,880 | promotion × store × SKU | yes | Promotion |

The segment-assignment alias is the only processed artifact without DVC ownership and has no active consumer. It is retained for audit and must not be mistaken for labeled training data.

## Quality systems

- PostgreSQL validation protects operational constraints and referential integrity.
- dbt tests protect warehouse relationships, key uniqueness and promotion boundary semantics.
- Great Expectations validates all eight published artifacts and their business keys/basic ranges.
- pytest protects feature timing, target semantics, modeling calculations, serialization and API dispatch.
- DVC owns seven processed datasets and seven canonical stages; it provides local reproducibility only because no remote exists.

Major gaps are end-to-end fresh-clone reproduction, live Kafka integration evidence, deployed Airflow execution, inference schema tests, service/load tests, drift monitoring and external-data validation.

## Repository hygiene, portability and README gaps

No tracked `.env`, credential or service-account file was found. `.env.example` is tracked and real `.env` files are ignored. No tracked file larger than 1 MB was found in the Git index; large datasets and canonical artifacts are DVC/ignore managed. Docker Compose contains development defaults, including a Grafana fallback password, which must never be treated as a production secret.

No developer-machine absolute path was found in repository-facing source, config or documentation. Absolute `C:\Users\Eclipse\...` paths do occur inside generated canonical manifests for Forecasting, Stockout and Promotion. They do not control execution, but should become repository-relative in a future artifact-portability cleanup.

README currently describes the platform but does not yet provide one authoritative table for all eight planned cores, the blocked Segment Assignment state, serving/offline decisions, DVC-remote limitation or cloud/template execution status. The final documentation phase should link this checkpoint instead of duplicating its details.

A fresh developer can inspect and install the repository, start PostgreSQL, rebuild local warehouse layers and run tests, but cannot retrieve DVC-owned processed data/canonical outputs from another machine because no DVC remote exists. Airflow/Airbyte/BigQuery execution also requires external runtime configuration.

## Safe Git checkpoint plan

Do not commit until the current cross-stage diff has been reviewed. Recommended dependency-aware sequence:

1. data-contract and warehouse changes: dbt promotion marts/tests, dataset builder, quality validation and processed-data DVC pointers;
2. shared modeling API/CLI and dependency changes;
3. Stockout Classification/Survival and their configs/tests/docs/artifacts metadata;
4. Segmentation and Anomaly implementations/configs/tests/docs;
5. Basket and Promotion implementations/configs/tests/docs plus DVC stages;
6. project-wide checkpoint registry, architecture, deployment, MLOps and portfolio documents;
7. final README/reproducibility cleanup after verifying a clean diff.

Each commit should include its matching `dvc.yaml`/`dvc.lock` changes and compact metrics, without committing ignored Parquet/model binaries directly.

## Infrastructure truth

- PostgreSQL, DuckDB/dbt and local dataset/quality pipelines have execution evidence.
- Kafka producer/consumer/DLQ/idempotency code and Docker profile exist, but the repository contains no durable runtime validation report. Treat it as an implemented demonstration, not production streaming.
- Airflow DAG exists but was not deployed or executed.
- Airbyte and BigQuery are configured but not executed.
- Grafana has a Compose profile but no verified monitoring deployment.

## Deferred backlog

| Item | Classification | Requirement |
|---|---|---|
| Segment Assignment | BLOCKED | stable/business-approved labels |
| Segmentation V2 | REQUIRES_REAL_DATA | more stores and longer history |
| Anomaly daily-grid V2 | V2_HYPOTHESIS | zero-event grid and reviewed labels |
| Forecast-residual anomaly | BLOCKED | compatible same-day forecast contract |
| Survival PH remediation | V2_HYPOTHESIS | time-varying effects or stratification plus more events |
| Stockout calibration | REQUIRES_REAL_DATA | matured labels and prevalence monitoring |
| Basket external validation | REQUIRES_REAL_DATA | real orders with business review |
| Promotion causal design | REQUIRES_REAL_DATA | valid controls/treatment assignment and campaign cost |

## Final decision

V1 modeling/analytics is complete with limitations. Forecasting and stockout classification should enter serving design. Survival, segmentation, anomaly, basket and promotion remain offline or scheduled analytics. Segment Assignment remains blocked. The next engineering phase is integrated serving/BI/MLOps architecture and repository checkpointing, not another analytical core.
