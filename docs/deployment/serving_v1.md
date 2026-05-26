# Frozen-model serving V1

Only Forecasting and Stockout Classification are served. Both load trusted joblib bundles once through `FrozenModelRegistry`; startup never fits, selects, or evaluates a model. Bundle features and targets must match canonical manifests. SHA-256 identities and safe metadata are exposed, never filesystem paths.

Forecasting predicts aggregate realized units in `(t,t+7d]` and clips negative output to zero. Stockout returns a score for occurrence in `(t,t+7d]`, the frozen threshold `0.7695666515458811`, and a risk flag; calibration remains limited. Outcome/future fields are rejected. Batch size is 1–1,000; larger work belongs in Python/CLI jobs.

`/health` means process liveness; `/ready` requires both trusted artifacts. MLflow is not a hard serving dependency. Survival, segmentation, anomaly, basket and promotion remain offline/read-only. Rollback is explicit artifact version selection; no silent fallback exists.

