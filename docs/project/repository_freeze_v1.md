# Repository Freeze & Reproducibility Checkpoint V1

## Scope and starting state

- Branch: `main`
- Starting HEAD: `d6f2d9d8a3c72bfb4ed75b102e43c7c49f9d2465`
- Starting dirty inventory: 20 modified tracked files and 43 untracked files.
- DVC: 3.63.0, seven independent stages, initially up to date, no remote configured.
- PostgreSQL: running locally in Docker and healthy.
- Safety: no push, reset, clean, restore, stash, rebase, amend, tag, DVC remote creation, model retraining, or DVC reproduction was performed.

## Change inventory

The accumulated state was classified into data/promotion contracts, DVC dataset pointers, stockout classification and survival, segmentation and anomaly, basket and promotion analytics, shared modeling/API/DVC infrastructure, project checkpoint evidence, and repository portability. Generated Parquet data, model binaries, databases, caches, logs, Docker state, and raw donor data remain outside Git. Segment Assignment remains blocked and has no model or DVC stage.

## Security and large-file audit

Path-only scans found no real token, API key, private key, service-account file, committed `.env`, or production credential. The README contains the word `password` only as documentation; Docker development fallback credentials are non-secret local defaults. No modified or untracked Git candidate exceeded 1 MB. DVC-managed datasets and canonical model directories were not staged as Git blobs.

## DVC ownership

| Dataset pointer | Consumer |
|---|---|
| `data/processed/forecasting/forecasting_v1.parquet.dvc` | Forecasting |
| `data/processed/stockout/stockout_v1.parquet.dvc` | Stockout Classification and Survival |
| `data/processed/segmentation/segmentation_v1.parquet.dvc` | Segmentation |
| `data/processed/anomaly/anomaly_v1.parquet.dvc` | Anomaly |
| `data/processed/basket/basket_v1.parquet.dvc` | Basket |
| `data/processed/promotion_daily/promotion_daily_v1.parquet.dvc` | Promotion analytical input |
| `data/processed/promotion_performance/promotion_performance_v1.parquet.dvc` | Promotion descriptive output |

Canonical outputs for Forecasting, Stockout Classification, Stockout Survival, Segmentation, Anomaly, Basket, and Promotion are declared by `dvc.yaml`. One `dvc.lock` necessarily records the accumulated seven-stage state. No DVC remote exists, so Git preserves pointers and pipeline metadata but a fresh machine cannot retrieve cache objects.

## Portability repair

Canonical forecasting, stockout, survival, and promotion manifest paths were changed from local absolute Windows paths to repository-relative paths. Serialization now uses repository-relative paths when artifacts are under the project root. DVC hashes were updated with `dvc commit --force`; no stage was reproduced and no model was retrained. Metrics, selected methods, thresholds, dataset fingerprints, and analytical results were unchanged. The only remaining absolute-path occurrence in repository-facing documentation is historical audit evidence explaining the repaired issue.

## Commits executed

1. `b3c55d6` — `feat(data): refine promotion analytical contracts`
2. `c4f3891` — `feat(stockout): add classification and survival V1`
3. `c49d466` — `feat(analytics): add segmentation and anomaly V1`
4. `c15a1e1` — `feat(analytics): add basket and promotion V1`
5. `cb1ca42` — `feat(modeling): expand experiment API and DVC pipeline`
6. `de77518` — `docs(project): add V1 modeling checkpoint`
7. `SELF` — `chore(repo): record repository freeze V1`; its exact SHA is the containing commit and is obtained with `git rev-parse HEAD`.

Every commit used explicit path staging and staged `--stat` plus `--name-status` inspection. Targeted tests passed before their corresponding commits.

## Validation

- pytest: 105 passed, 0 failed, 4,358 warnings, 113.13 seconds.
- dbt: 19 table models, 8 view models, and 28 tests; PASS=55, WARN=0, ERROR=0, SKIP=0; 4.18 seconds.
- Great Expectations: all eight published dataset artifacts passed.
- DVC: `status` reports data and pipelines up to date; seven stages appear in the DAG; metrics load successfully; doctor reports DVC 3.63.0 and no remotes.
- PostgreSQL: Docker reports PostgreSQL 17 healthy; database validation passed for all 18 operational tables, constraints, reconciliation checks, and smoke queries.

## Scientific freeze

The frozen registry remains authoritative: Forecasting test WAPE 0.3778884755; Stockout Classification test average precision 0.2551216857; Stockout Survival concordance 0.7922890233; Segmentation k=3 and silhouette 0.3307169762; Anomaly Isolation Forest candidate rate 0.0241503797; Basket 1,262 canonical rules with Apriori/FP-Growth consistency; Promotion descriptive units change fraction 0.0621638304. Segment Assignment remains `BLOCKED`/`NOT_READY`. These are synthetic, short-history V1 results and are not production claims.

## Remaining gaps

- No DVC remote; cache retrieval from a fresh machine is unavailable.
- Clean-machine reproduction has not been tested and is not claimed.
- Serving, BI delivery, production monitoring, and deployed orchestration remain absent.
- Segment Assignment remains scientifically blocked.
- Deprecation/runtime warnings remain in third-party numerical and plotting libraries.

For a portfolio repository, an S3-compatible object store is the preferred DVC remote because it supports durable, automatable access without coupling large artifacts to GitHub. Google Drive is simpler for a single-user demonstration but weaker for automation. A local filesystem remote does not establish cross-machine reproducibility. No remote was configured in this checkpoint.

No push or tag was performed.
