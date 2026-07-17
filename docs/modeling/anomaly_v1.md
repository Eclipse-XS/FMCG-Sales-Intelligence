# Sales Anomaly Detection Modeling V1

Sales Anomaly Detection V1 ranks unusual observed positive-sales events. It is post-event analytics, not forecasting, and there are no independently verified anomaly labels. Flags are candidates for review, not confirmed fraud, errors, incidents, or business anomalies.

## Data and scoring semantics

The source grain is `event_date × store_id × sku_id`. It contains positive realized sales events only; absent zero-sale days are not rows. The current observed units, transaction price, and promotion state are available when scoring. Historical statistics use positive events for the same store–SKU in `[t-7 days,t)` and therefore exclude the current and all future observations.

Rows with fewer than two historical positive events are `NOT_SCORABLE_INSUFFICIENT_HISTORY` for the z-score. A zero historical standard deviation produces zero when the current value equals the constant history and signed infinity when it differs. The latter is an explicit deterministic candidate condition.

## Methods

The transparent baseline is a signed historical rolling z-score with `|z| >= 3`. Direction is retained as `HIGH` or `LOW`.

Isolation Forest is the only nonlinear candidate. Median imputation with missing indicators and scaling are fitted on the configured historical reference period, followed by Isolation Forest fitted on the same rows. Later observations are scored without refitting. The canonical project score is `-decision_function`, so larger values mean more unusual observations. Contamination is a predeclared operational threshold policy, not a tuned performance parameter.

Method overlap is reported as agreement, never precision, recall, accuracy, F1, or ROC-AUC. Consecutive flagged dates for the same store–SKU are grouped into runs.

## Forecast residual compatibility

Forecasting V1 predicts total realized demand over `(t,t+7]`; anomaly V1 scores a current positive daily sales event. These grains and outcome horizons are incompatible. No Forecasting V1 retraining or residual join is performed.

## Limitations

The data are synthetic, cover about 90 days, omit zero-sale days, and have no verified anomaly labels. Thresholds mechanically affect candidate rates. Promotion and other context can explain unusual observations. Inventory-censoring context is unavailable in this event artifact. Results are offline diagnostics without production validation.

## Reproduction

```powershell
.venv\Scripts\python.exe -m fmcg_sales_intelligence.science.cli run --task anomaly --output artifacts/canonical/anomaly_v1 --experiment-id anomaly_v1_canonical --overwrite
```
