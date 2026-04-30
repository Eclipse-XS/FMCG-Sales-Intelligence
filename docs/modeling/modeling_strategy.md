# Modeling and evaluation strategy

## 1. Purpose and scope

This document freezes the modeling contract before any estimator is fitted. It is grounded in the current Parquet artifacts and EDA run `20260916T145342862436Z_666fd9c828_653db2`. This phase does not train, tune, rank, or serialize models and does not change data semantics.

## 2. Current data readiness

| Task | Artifact | Rows / independent units | Dates | Readiness |
|---|---|---:|---|---|
| Forecasting | `forecasting_v1.parquet` | 86,400; 960 store–SKU series | 2024-01-01–2024-03-30 | READY WITH LIMITATIONS |
| Stockout | `stockout_v1.parquet` | 17,280; 73 episodes in 44 warehouse–SKU series | 2024-01-01–2024-03-30 | READY WITH LIMITATIONS |
| Segmentation | `segmentation_v1.parquet` | 60 rows; 20 stores × 3 snapshots | 2024-01-31–2024-03-30 | READY WITH LIMITATIONS |
| Segment assignment | compatibility alias only | no cluster labels | — | NOT READY |
| Anomaly | `anomaly_v1.parquet` | 35,032 positive-sale events | 2024-01-01–2024-03-30 | READY WITH LIMITATIONS |
| Basket | `basket_v1.parquet` | 24,370 lines; 2,000 orders; 48 SKUs | 2024-01-01–2024-03-30 | READY |
| Promotion | `promotion_performance_v1.parquet` | 2,880 promotion–store–SKU rows | 2024-01-01–2024-03-30 | READY WITH LIMITATIONS |

Forecasting contains 79,680 complete targets (92.22%), 51,368 realized zero-sales observations, 242 inventory-censored observations, and 159,099 / 157,604 / 1,495 requested / realized / lost units. Stockout contains 548 positive horizons, but these derive from 73 physical episodes; rows are not independent.

## 3. Global modeling principles

1. Features are frozen at the documented scoring timestamp. Future targets, target-observability fields, realized future inventory and delivery outcomes are forbidden.
2. Learned imputers, scalers, encoders, feature selectors and dimensionality reducers are fitted only on the training partition or reference population.
3. Temporal tasks use chronological partitions. Random row splits are prohibited.
4. Validation is used for model choice, hyperparameters and decision thresholds. Test is evaluated once after the candidate and threshold are frozen.
5. Every predictive experiment must beat a meaningful naïve/business baseline. Statistical uncertainty, temporal-fold consistency and slice behavior matter; a single aggregate metric cannot select a model.
6. Persist random seed `20260916`, split boundaries, configuration, dataset SHA-256, EDA run ID and code revision when available.
7. Candidate algorithms represent distinct assumptions. Deep sequence models are excluded: 90 days do not justify their complexity.

## 4. Feature taxonomy and identifier policy

Integer IDs are nominal keys, never continuous quantities.

| Feature class | Examples | Default treatment |
|---|---|---|
| Continuous | price, rolling mean/std, ratios, revenue | numeric; scaling for linear/distance models |
| Count | lags, units, inventory, velocity, replenishment | numeric; consider skew, never reinterpret null as zero without contract |
| Categorical | brand, category, store type, channel | one-hot for linear models; native categorical handling where supported |
| Binary | scheduled promotion, event promotion | Boolean; exclude zero-variance fields |
| Temporal | prediction/event/snapshot/order date | split/group key; derived calendar features only if available at scoring |
| Identifier | store, SKU, warehouse, promotion, order, region IDs | group/join/slice key or categorical entity feature, never scaled numeric |
| Target | future units, stockout event/time | outcomes only |
| Forbidden/post-event | future stockout date, target observability, forecast residual before forecasting exists | excluded |

`store_id` and `sku_id` may be categorical features for within-universe forecasting but are excluded from cold-start claims. `warehouse_id` and `sku_id` are categorical for stockout. `order_id` is transaction structure only. `promotion_id` is grouping/slicing context, not an ordinal regressor. `region_id` is categorical context.

## 5. Missing-value policy

- Structural history: null lags and rolling values before enough history exists. Linear models use train-fitted median imputation plus missing indicators. Tree/native-categorical models may retain supported missing values. Zero is not an imputation because it means observed zero demand.
- Target unavailable: forecasting rows with `target_observed_next_7d=false` are excluded; stockout no-event rows with incomplete horizons are excluded from ordinary binary evaluation. Outcomes are never imputed.
- Genuine missingness: investigate and fail required-field checks before modeling.
- Promotion boundary nulls are “window unavailable,” not zero uplift.
- Anomaly lag nulls are structural: `lag_1` 19,346, `lag_7` 20,290, rolling mean 2,132, rolling std 6,696. Preserve indicators or restrict analyses requiring a complete reference window.

## 6. Temporal validation and overlapping windows

Both supervised targets cover `(t,t+7]`. Adjacent labels overlap and ordinary row-wise confidence intervals exaggerate effective sample size. Partitions use contiguous anchor dates with a seven-day embargo so outcome windows cannot overlap across partitions.

| Partition | Anchor dates | Forecast rows | Stockout evaluable rows | Positive horizons | Episode starts in anchor period |
|---|---|---:|---:|---:|---:|
| Selection train | 2024-01-01–2024-02-04 | 33,600 | 6,720 | 166 | 17 |
| Embargo | 2024-02-05–2024-02-11 | excluded | excluded | — | — |
| Validation | 2024-02-12–2024-02-25 | 13,440 | 2,688 | 74 | 8 |
| Final train | 2024-01-01–2024-02-25 | 53,760 | 10,752 | 281 | 32 |
| Embargo | 2024-02-26–2024-03-03 | excluded | excluded | — | — |
| Test | 2024-03-04–2024-03-23 | 19,200 | 3,840 | 186 | 27 |

For forecasting, selection uses the first train/validation pair. After selection, refit on final-train dates and evaluate once on test. Rows through March 23 have complete seven-day targets; March 24–30 are excluded.

For stockout, the same physical episode may last up to five days and appear in adjacent horizon labels. In addition to the date embargo, assign each zero-inventory run an analytical episode ID and purge any episode touching both sides of a boundary. Report row-level and episode-level bootstrap uncertainty. Validation has only eight episode starts, so threshold/model selection is intrinsically noisy and must stay simple.

## 7. Forecasting contract

### Target

Primary: `target_units_next_7d`, realized sales summed over `(t,t+7]`. It answers operational sales/revenue and supply-constrained planning. It is selected because it is directly tied to observed transactions and only 242/86,400 daily observations are inventory-censored.

Secondary: `target_requested_demand_next_7d`. It answers unconstrained customer demand and must be a separate experiment. `target_lost_sales_next_7d` is diagnostic, not merged into the primary target.

### Features

Allowed core features are exact lags 1/7/14/28, rolling mean/std and velocity over `[t-7,t)`, scheduled price, categorical store/SKU/region/brand/category/store type/channel. `censored_days_prior_7d` is an explicitly synthetic, optional experiment. `scheduled_is_promo` is currently constant true and is excluded unless future data provides variation. Targets and target-observability columns are forbidden features.

### Baselines

- Zero: `ŷ(t)=0`; a lower bound relevant to intermittency.
- Last-value scaled: `ŷ(t)=7 × realized_sales(t−1)`.
- Trailing mean/sum: `ŷ(t)=Σ realized_sales(d), d∈[t−7,t)`.
- Prior-week seasonal: the same `[t−7,t)` sum, interpreted as the immediately preceding comparable seven-day window. With only 90 days, no annual seasonal baseline is valid.

The two seven-day formulations coincide in the current feature horizon; implementation should store one prediction and two semantic labels, not double-count it as two independent baselines.

### Models and preprocessing

1. Ridge regression: train-only median imputation, missing indicators, standard scaling for numeric features, one-hot categorical encoding.
2. Poisson regression: same preprocessing, log link and nonnegative predictions; compare only if convergence and dispersion diagnostics are acceptable.
3. CatBoost regressor: one nonlinear candidate with native categorical handling and missing values. No LightGBM/XGBoost duplicate model zoo.

### Metrics

Primary WAPE: `Σ|y−ŷ| / Σ|y|` over the evaluation block; undefined blocks with zero total demand are reported as unavailable. Secondary: MAE, RMSE, and signed bias `Σ(ŷ−y)/Σy`. Clip physically impossible negative predictions to zero only as a documented prediction policy, while also auditing raw predictions. MAPE is prohibited because zeros are legitimate. R² is diagnostic only.

Report metrics by store, SKU, category, channel, demand-volume band, promotion status where variable, intermittent-series band and inventory-censored context. Improvement requires better validation WAPE than the strongest naïve baseline, no material bias deterioration, reasonable fold/slice stability, and confirmation on untouched test—not an arbitrary percentage threshold.

## 8. Stockout classification contract

Target is `stockout_within_7d`: first `available_quantity<=0` in `(t,t+7]`. Include positives as soon as observed; include no-event rows only when `horizon_complete=true`. Exclude `first_stockout_date`, event/censor times, horizon completeness and label columns from features.

Business baselines:

- always no stockout, retained only to expose why accuracy is misleading;
- alert when `available_quantity <= reorder_point`;
- alert when `available_quantity <= safety_stock`;
- days-of-cover alert using available stock divided by historical `sales_velocity_7d`, with zero velocity handled as no finite depletion estimate.

First ML baseline is class-weighted logistic regression with train-only imputation/scaling and categorical one-hot encoding. One nonlinear candidate is histogram gradient boosting with train-derived categorical encoding. No SMOTE: it would duplicate dependent horizons, not create episodes.

Primary metric is Average Precision/PR-AUC. Secondary metrics are precision, recall, F1, ROC-AUC and Brier score. Select the operating threshold on validation only and report the full precision–recall tradeoff. Accuracy is never a selection metric.

Episode-level diagnostics: episode warned before onset, first-warning lead time, episodes missed, alerts outside pre-episode windows, and alert runs rather than raw alert rows. Slice false positives/negatives by warehouse, SKU and inventory state.

## 9. Stockout survival contract

Time origin is snapshot `t`; scale is days. `event_observed=true` uses `event_time_days` to the first stockout in `(t,t+7]`. Otherwise `censor_time_days` is the observed follow-up, with `horizon_complete` distinguishing administrative end censoring. This is a discrete, short-horizon survival representation—not lifetime inventory survival.

Kaplan–Meier is the descriptive reference. Cox proportional hazards is the only initial regression candidate, conditional on proportional-hazards diagnostics and episode-aware uncertainty. Concordance index and Brier score over days 1–7 are allowed. With 73 episodes and one terminal right-censored physical episode, complex survival forests/neural survival models are unjustified. A longer-horizon event table is scientifically preferable later but is not silently introduced here.

## 10. Store segmentation and segment assignment

The primary clustering population is the latest snapshot, 2024-03-30: 20 independent stores. Earlier snapshots evaluate stability; treating all 60 rows as independent would overweight repeated stores. Core numeric features are floor area, revenue, units, profit, active SKUs, average price, promotion share and revenue volatility. Robust scaling is fitted on the primary snapshot. Region/store type/channel remain context for interpretation; they are not blindly one-hot encoded into Euclidean geometry.

KMeans is the baseline; agglomerative clustering is the single alternative. Evaluate candidate `k=2..5` using silhouette, Davies–Bouldin, minimum/maximum cluster size, bootstrap/perturbation stability, snapshot migration and business interpretability. No metric alone selects `k`; HDBSCAN is excluded because 20 stores are insufficient for reliable density geometry.

Segment assignment remains NOT READY. Clustering must first persist model/preprocessing artifacts, cluster definitions, latest-snapshot pseudo-labels, stability evidence and a versioned label contract. Those labels are pseudo-labels, not ground truth. Only then may a supervised assignment classifier be specified.

## 11. Anomaly detection

This is post-event, unsupervised detection. The baseline is a historical rolling z-score using only prior reference values. Isolation Forest is the sole multivariate candidate. LOF may be used only as an offline local-neighborhood sensitivity check because it lacks a natural stable future-scoring interface without novelty mode and careful reference handling.

There are no verified labels; accuracy, precision, recall and F1 are prohibited. Evaluate score distribution, candidate rate, temporal and slice stability, and manual/business review. Forecast-residual anomalies become a distinct downstream contract only after out-of-sample forecasting predictions exist. No anomaly labels are generated here.

## 12. Market basket analysis

Represent each `order_id` as a set of SKU presences; quantity is retained for descriptive analysis but not repeated as duplicate items. Current monthly order counts are January 675, February 660 and March 665. Analyze SKU, brand and category item levels separately.

Apriori is the transparent baseline; FP-Growth is the scalable alternative. Support is the fraction of orders containing an itemset, confidence is `P(consequent|antecedent)`, and lift is confidence divided by consequent prevalence. Minimum thresholds must be derived from empirical item frequency and desired minimum supporting order count, then frozen. Compare rule support/rank across months; do not use random order splits.

## 13. Promotion analysis

This remains descriptive. Report baseline, promo and post units; absolute uplift; percentage uplift only for nonzero baselines; promo revenue and profit; and slices by promotion, store type, region and channel. Promotion 1 has no baseline window for 960 rows; promotion 3 has no post window for 960 rows; these are unavailable, not zeros.

A future regression predicting promo-period sales answers a predictive question. It does not estimate causal lift. Causal claims require credible untreated controls, treatment-timing assumptions, overlap and a design such as difference-in-differences with diagnostics. None exists now.

## 14. Preprocessing by model family

- Linear/logistic/Poisson: train-only imputation, missing indicators, scaling, one-hot categorical encoding; regularization applied after transformation.
- Histogram tree models: no scaling; missing handling is model-specific; categorical encoding must be fitted on train and map unseen levels explicitly.
- CatBoost: native categorical strings/IDs, no numeric interpretation of IDs, train-only category statistics.
- KMeans/agglomerative: robust/standard scaling is mandatory; correlated revenue/units/profit features require sensitivity analysis.
- Isolation Forest: numeric/context encoding defined from the reference period; scaling is not mathematically mandatory for axis-aligned isolation but is retained for consistent preprocessing diagnostics.

## 15. Cold-start limits

All temporal partitions contain the same 20 stores and 48 SKUs. Current evaluation measures future dates for known entities only. It does not establish performance for unseen SKUs, unseen stores or new store–SKU pairs. Entity-ID models must include an explicit unknown category, but that is operational robustness, not validated cold-start skill. Future evaluation needs held-out-entity splits and content attributes with adequate variation.

## 16. Error analysis and explainability

Forecasting error analysis is mandatory by SKU, store, category, channel, demand volume, intermittency, promotion context and censoring context. Stockout analysis covers false positives/negatives, missed episodes, warning lead time, warehouse, SKU and inventory state.

Report Ridge/logistic coefficients only after transformation and with correlated-feature warnings. Tree models require held-out permutation importance. SHAP is optional only if a selected nonlinear model creates a specific local-explanation need; it is not a default dependency and must not be interpreted causally.

## 17. Experiment artifacts and comparison

Future runs use:

```text
artifacts/experiments/<task>/<experiment_id>/
    manifest.json
    config.yaml
    metrics.json
    predictions.parquet
    model/
    figures/
    report.md
```

The manifest records experiment/task IDs, dataset and schema fingerprints, EDA run, target/features/exclusions, split and embargo, preprocessing, estimator/hyperparameters, seed, metrics/slices, artifact paths, timestamp and code revision. Test predictions are immutable once published.

Candidate selection requires baseline improvement on validation, temporal stability, slice behavior, bias/calibration, uncertainty and complexity review. Test cannot break ties among repeatedly tuned candidates. Forecast selection prioritizes WAPE and bias; stockout prioritizes Average Precision, calibration and episode-warning behavior.

## 18. Dependency graph and implementation order

```text
Forecasting ──> out-of-sample residuals ──> residual anomaly contract

Segmentation ──> cluster pseudo-label artifact ──> Segment Assignment

Stockout Classification ─┐
                         ├── share source contract, remain distinct tasks
Stockout Survival ────────┘

Basket and Promotion descriptive analysis are independent.
```

Recommended order:

1. Shared experiment manifest, split utilities, metrics and prediction artifact contracts.
2. Forecasting naïve baselines, then Ridge/Poisson and one CatBoost candidate.
3. Stockout business rules and logistic classification; add one boosting candidate only if validation supports it.
4. Kaplan–Meier and conditional Cox survival analysis.
5. Latest-snapshot segmentation plus stability assessment.
6. Anomaly statistical baseline and Isolation Forest; residual analysis waits for forecasting.
7. Basket rules and monthly stability.
8. Promotion descriptive analysis.
9. Segment assignment only after accepted cluster pseudo-labels exist.

## 19. Remaining scientific limitations

Only 90 days are available; annual seasonality and robust multi-fold backtesting are impossible. Forecast labels overlap. Stockout validation has only eight episode starts and synthetic event mechanics. Promotions have universal scheduled coverage within each monthly promotion and missing boundary windows. Segmentation has 20 independent entities. Anomaly labels and causal promotion controls do not exist. These limitations must be carried into every experiment report.
