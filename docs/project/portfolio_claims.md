# Portfolio Claim Audit

## SAFE_TO_CLAIM

- Built a local end-to-end FMCG analytics platform using PostgreSQL, DuckDB, dbt, Polars, Great Expectations, DVC and automated tests.
- Implemented seven independently reproducible V1 analytical/modeling stages.
- Implemented leakage-aware seven-day demand forecasting and stockout-risk modeling contracts.
- Preserved observed-zero versus unobservable-boundary semantics in promotion analytics.
- Persisted canonical manifests, metrics, diagnostics, reports and serialized model state where applicable.

## CLAIM_WITH_LIMITATION

- Forecasting outperformed its trailing-window baseline on a short synthetic holdout; the first technical final-test attempt read the test set before failing during downstream artifact construction.
- Stockout classification achieved AP 0.255 on rare synthetic events but detected 15 of 33 test episodes and needs calibration monitoring.
- Survival modeling achieved C-index 0.792 on a small, highly censored cohort with a PH-assumption violation.
- Store clustering produced coherent internal geometry, but only 20 stores and 52.5% temporal retention make labels exploratory.
- Anomaly detection produces stable candidate rankings, not validated anomalies.
- Association mining produces reproducible synthetic co-occurrence rules, not a production recommender.
- Promotion analysis reports matched-window observed differences, not causal effects.
- Kafka replay, Airflow, Airbyte, BigQuery and Grafana assets demonstrate architecture intent; runtime status varies and must be stated explicitly.

## DO_NOT_CLAIM

- Production-ready platform or deployed MLOps system.
- Real corporate Coca-Cola results.
- Causal promotion optimization, causal uplift or ROI.
- Stable production customer/store segments or a Segment Assignment classifier.
- Confirmed anomaly detection accuracy.
- Production recommender system.
- Operational Airflow, Airbyte, BigQuery or model-monitoring deployment.
- Exactly-once production CDC pipeline.
