# Scientific Cores Summary

| Core | Task | Method | Primary Metric | Primary Metric Value | Secondary Metrics | Dataset | Artifact Version | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Forecasting | Supervised regression | catboost_regressor | Test WAPE | 0.3778884755200097 | MAE=5.13108; RMSE=6.909 | data/processed/forecasting/forecasting_v1.parquet | forecasting_v1 | READY_WITH_LIMITATIONS |
| Stockout Classification | Binary classification | histogram_gradient_boosting | Test average precision | 0.2551216856988334 | ROC AUC=0.799097; Brier=0.0634611 | data/processed/stockout/stockout_v1.parquet | stockout_classification_v1 | READY_WITH_LIMITATIONS |
| Stockout Survival | Time-to-event analysis | cox_l2_0.1 | Test concordance index | 0.7922890233095247 | Mean supported-horizon Brier=0.0291519 | data/processed/stockout/stockout_v1.parquet | stockout_survival_v1 | READY_WITH_LIMITATIONS |
| Segmentation | Unsupervised clustering | kmeans | Silhouette | 0.3307169762039364 | Davies-Bouldin=0.9043; retention=52.50% | data/processed/segmentation/segmentation_v1.parquet | segmentation_v1 | READY_WITH_LIMITATIONS |
| Anomaly Detection | Unsupervised candidate detection | isolation_forest | Isolation Forest candidate rate | 0.024150379683804308 | Candidates=388; method Jaccard=0.0172499 | data/processed/anomaly/anomaly_v1.parquet | anomaly_v1 | READY_WITH_LIMITATIONS |
| Market Basket Analysis | Association-rule mining | fp_growth | Canonical rule count | 1262.0 | Stable rules=94; FP-Growth/Apriori consistent=True | data/processed/basket/basket_v1.parquet | basket_v1 | READY_WITH_LIMITATIONS |
| Promotion Performance | Descriptive comparison | DESCRIPTIVE_PROMOTION_ANALYSIS | Aggregate descriptive units change | 0.06216383035005745 | Eligible exposures=1920; baseline sign stability=79.69% | data/processed/promotion_daily/promotion_daily_v1.parquet; data/processed/promotion_performance/promotion_performance_v1.parquet | promotion_v1 | READY_WITH_LIMITATIONS |
