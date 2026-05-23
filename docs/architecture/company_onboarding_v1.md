# Company onboarding V1

1. Copy `domain_packs/_template` and assign a profile/version.
2. Register CSV, Parquet, database export, or current canonical source.
3. Map source columns declaratively before feature logic.
4. Validate required fields, nulls, keys and domain constraints.
5. Normalize to the versioned contracts in `contracts/registry_v1.yaml`.
6. Run dbt/Great Expectations/pytest quality gates as applicable.
7. Evaluate capability availability; absent concepts remain unavailable.
8. Build only supported task datasets.
9. Run training explicitly through offline CLI/batch workflows, never an HTTP side effect.
10. Track future experiments in MLflow while DVC owns data/artifact reproducibility.
11. Review and freeze approved artifacts.
12. Serve predictive cores or publish caveated offline analytics.

The file-validation API is for bounded normalized examples. Enterprise-scale onboarding belongs in database/object-store jobs. A direct SAP connector is not implemented; use reviewed SAP export files.

