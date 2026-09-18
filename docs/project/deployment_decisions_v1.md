# Deployment Decisions V1

| Core | Mode | State required | Cadence | Input | Output | BI | Monitoring | Review |
|---|---|---:|---|---|---|---:|---|---:|
| Forecasting | SCHEDULED_BATCH_INFERENCE | CatBoost joblib | daily/weekly | point-in-time store-SKU features | seven-day units forecast | yes | WAPE, bias, distribution and feature drift | no |
| Stockout classification | SCHEDULED_BATCH_INFERENCE | HGB joblib + threshold | daily/event-triggered | current inventory and prior velocity | probability, threshold flag, risk context | yes | prevalence, AP after maturity, Brier/calibration, alert volume, episode detection | operational alerts |
| Stockout survival | OFFLINE_ANALYTICS | Cox joblib | on-demand | at-risk inventory rows | survival/risk curves | no initially | event/censoring counts, PH diagnostics, C-index/Brier | yes |
| Segmentation | HUMAN_REVIEW_ANALYTICS | KMeans joblib | monthly/on-demand | reviewed store snapshot | exploratory labels/profiles | profiles only | cluster size, feature drift, retention/ARI | required |
| Segment assignment | BLOCKED | none approved | none | no valid target | none | no | readiness only | required |
| Anomaly | HUMAN_REVIEW_ANALYTICS | Isolation Forest joblib | daily batch | observed post-event rows | ranked candidates and scores | yes | candidate rate, score drift, agreement, reviewer outcomes | required |
| Basket | OFFLINE_ANALYTICS | none | monthly/on-demand | completed orders | itemsets/rules | yes | basket volume, support drift, rule stability | required |
| Promotion | OFFLINE_ANALYTICS | none | after windows mature | complete promotion daily grid | descriptive eligible comparisons | yes | completeness, overlap, price coverage, baseline sensitivity | required |

Predictive serving design must add model loading, version metadata, strict request/response schemas, point-in-time feature retrieval, batch prediction, health/readiness checks, error handling and inference validation. FastAPI, ONNX and a dedicated service are not yet implemented. ONNX is optional: existing joblib formats are adequate for a controlled Python service, while conversion would add validation obligations without a demonstrated deployment constraint.

Conceptual BI marts:

- `mart_forecast_monitoring`
- `mart_stockout_risk`
- `mart_anomaly_review`
- `mart_basket_rules`
- `mart_promotion_performance`
- `mart_segmentation_profiles` only with explicit exploratory status

Retraining is evidence-triggered, not calendar-driven. Forecasting requires matured error degradation or material feature/schema drift. Stockout classification requires matured-label AP/calibration degradation, prevalence shift or policy change. Survival requires more physical events and PH remediation. Unsupervised/offline cores should be recomputed only when source coverage or business review warrants it.
