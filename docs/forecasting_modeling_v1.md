# Forecasting Modeling V1

The production-like experiment entry point is `python -m fmcg_sales_intelligence.science.cli run --task forecasting`. The Python API is `fmcg_sales_intelligence.science.run_experiment`.

Prediction time is the start of day `t`. The target is total observed units in `(t,t+7 days]`. Only the approved pre-event core features in `config/modeling/forecasting.yaml` are supplied to estimators. Realized same-day outcomes and all target/observability fields are excluded. The two optional experimental fields are deliberately excluded from V1.

Model selection uses only the validation interval and WAPE. If candidates are within 0.5% relative WAPE, the deterministic simplicity order is Ridge, Poisson, CatBoost. The chosen specification is persisted before test access. The chosen estimator is then fit from scratch on the final-training interval and evaluated once on test. All negative predictions are clipped to zero.

Each normal API run creates a collision-safe immutable directory under `artifacts/experiments/forecasting/`. The DVC stage writes the same complete contract to the stable `artifacts/canonical/forecasting_v1/` output so it can be reproduced and versioned without encoding timestamps in `dvc.yaml`.

DVC tracks the ML-ready forecasting Parquet and the stable canonical experiment output. Source code, configuration, PostgreSQL state, raw source archives, and ad-hoc timestamped experiments remain outside DVC. No DVC remote is configured; therefore this repository provides local reproducibility but not yet cross-machine artifact transfer.

The artifact contains manifest, frozen selection, resolved config, validation/test metrics, DVC scalar metrics, test predictions, slice metrics, serialized final model, diagnostics, figures, and report. `final_model.joblib` bundles preprocessing metadata and supports inference with `fmcg_sales_intelligence.science.forecasting.predict_saved`.

## Final-evaluation incident record

The first final-evaluation process computed test metrics and then failed while constructing the residual column because the Parquet outcome was represented as `Decimal` and the prediction as `float`. The canonical rerun retained the same frozen selection, configuration and random seed; the only correction was explicit numeric type compatibility for the outcome. This means the canonical experiment contains one successful final evaluation, while the test partition was also read by the aborted technical attempt. The historical manifest remains unchanged and correctly records that the experiment predated the first Git commit.
