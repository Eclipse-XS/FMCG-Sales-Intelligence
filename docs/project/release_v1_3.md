# FMCG Sales Intelligence v1.3.0

This release packages the validated project as a reproducible portfolio system without changing frozen scientific results.

## Included

- Seven frozen analytical cores and FastAPI serving for forecast, stockout risk, and experimental cluster membership.
- React dashboard, PostgreSQL operational model, DuckDB/dbt warehouse, and Great Expectations contracts.
- DVC Google Drive restoration and MLflow canonical-run metadata.
- Docker Compose runtime, Prometheus/Grafana, optional Kafka replay, and bounded Airflow validation.
- Consolidated V1.3 repository structure with one Python package.
- GitHub clean-clone plus DVC restoration, hash identity, and exact serving-parity proof.

## Scientific evidence

Persisted results remain: forecast WAPE 0.3778884755; stockout AP 0.2551216857; survival C-index 0.7922890233; segmentation `k=3`, silhouette 0.3307169762; anomaly candidate rate 0.0241503797; 1,262 basket rules; descriptive promotion change 0.0621638304.

## Limitations

Data is synthetic or from public statistical donors. Cluster taxonomy stability is limited; membership is exploratory and supervised classification is not justified. Kafka and Airflow are local demonstrations. Production authentication, TLS, and distributed controls are absent. Airbyte/BigQuery are templates. Promotion results are descriptive, not causal. Repository licensing requires an explicit owner decision.

See the [license and attribution audit](license_and_attribution_audit_v1_3.md) and [repository hygiene report](repository_hygiene_v1_4.md).
