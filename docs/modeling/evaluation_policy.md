# Evaluation policy

Temporal supervised experiments use the boundaries in the machine-readable contracts. Seven-day prediction windows require a seven-day anchor embargo. Stockout additionally applies an analytical episode-aware purge so a physical zero-inventory run cannot occur on both sides of a split.

Validation is used for candidate, hyperparameter and threshold decisions. Final-train may include the validation period after choices are frozen. Test is evaluated once. Any subsequent design change invalidates the final-test designation and requires a new future holdout.

Metrics are reported at their natural dependence unit. Forecasting includes aggregate and series/slice results with block or series-aware uncertainty. Stockout includes row-level ranking/calibration and episode-level warning behavior. Unsupervised, basket and promotion tasks use stability and descriptive/domain criteria rather than fabricated supervised metrics.

Model comparison requires a meaningful baseline, multiple metrics, temporal stability, slice analysis, error analysis, calibration/bias where applicable, and a complexity review. “Best” cannot mean the smallest value of one metric on one test block.
