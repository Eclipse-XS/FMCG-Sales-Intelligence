# Current project status

Current checkpoint: **Repository Structural Consolidation V1.3**.

- Scientific core: frozen V1; persisted metrics and serving outputs unchanged.
- Repository: one Python package, consolidated `config`, `platform`, `artifacts/reports`, categorized tests, and developer `tools`.
- Runtime: PostgreSQL, FastAPI, frontend, MLflow, Prometheus, Grafana and Kafka validated locally; Airflow validated as a bounded ephemeral orchestration demo.
- Reproducibility: DVC Google Drive remote synchronized; GitHub clone plus DVC restoration and exact serving parity proven.
- Segment membership: frozen KMeans assignment is experimental and active; supervised segment classification remains `DEFERRED_NOT_JUSTIFIED_V1`.

Evidence:

- [Scientific checkpoint](modeling_checkpoint_v1.md)
- [Clean-clone reproducibility](clean_clone_reproduction_v1.md)
- [Runtime validation V1.2](runtime_platform_validation_v1_2.md)
- [Technology registry](../../artifacts/project/technology_registry_v1.json)
- [Segment assignment resolution](../modeling/segmentation_v1.md)
- [Repository structure V1.3](../architecture/repository_structure_v1_3.md)
- [V1.3 migration report](repository_structural_consolidation_v1_3.md)
