# Modeling feature policy

The authoritative task lists are the YAML contracts under `config/modeling/`; this document explains enforcement.

- A target or target-observability column may never appear in `features`.
- Date and entity keys remain identifiers even when also declared categorical.
- Integer storage type does not make an ID continuous.
- Same-day realized forecasting outcomes and future stockout fields are forbidden.
- Optional/experimental features require a separate ablation and a business availability statement.
- Zero-variance columns are removed based on training data and recorded; currently `scheduled_is_promo` is constant.
- Structural null history is represented through train-fitted imputation plus indicators when the estimator cannot handle nulls.
- All learned encoders, imputers, scalers and selectors are fitted inside the training pipeline.
- Unknown categories map to an explicit unknown level; this does not establish cold-start performance.
