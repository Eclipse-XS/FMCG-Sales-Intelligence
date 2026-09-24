# FMCG Sales Intelligence Integration / Usage Showcase

These examples show the supported product boundary. They load frozen artifacts and read-only outputs;
they do not train models, rebuild canonical artifacts, or use DVC/MLflow as serving APIs.

## Capability matrix

| Capability | Integration mode | Python API | REST API | Input | Output | Frozen artifact | Example |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Forecasting | Online/batch serving | `ForecastService.predict` | `POST /api/v1/predict/forecast` | 15 engineered V1 features | Non-negative 7-day unit forecast | `forecasting_v1/models/final_model.joblib` | Both clients, notebook |
| Stockout Classification | Online/batch serving | `StockoutService.predict` | `POST /api/v1/predict/stockout` | 11 inventory/replenishment features | Probability, threshold, risk flag | `stockout_classification_v1/models/final_model.joblib` | Both clients, notebook |
| Stockout Survival | Offline analytical scoring | `science.survival.predict_bundle` | No survival route | Five cohort features; task dataset required | Risk score and survival probabilities by horizon | `stockout_survival_v1/models/final_model.joblib` | Python client, notebook |
| Segmentation | Exploratory frozen membership assignment | `SegmentMembershipService.assign` | `POST /api/v1/analytics/segments/assign` | Four 30-day store features | Pseudo-label, distance, review metadata | `segmentation_v1/models/final_model.joblib` | Both clients, notebook |
| Anomaly Detection | Offline human-review analytics | `AnalyticsReadService.read("anomalies")` | `GET /api/v1/analytics/anomalies` | Built anomaly task dataset for recomputation; none for frozen-output reads | Ranked unreviewed candidates | `anomaly_v1/predictions_or_scores/review_candidates.csv` | Both clients, notebook |
| Market Basket Analysis | Offline human-review analytics | `AnalyticsReadService.read("basket-rules")` | `GET /api/v1/analytics/basket-rules` | Built basket task dataset for recomputation; none for frozen-output reads | Association rules | `basket_v1/outputs/association_rules.parquet` | Both clients, notebook |
| Promotion Performance | Offline descriptive analytics | `AnalyticsReadService.read("promotions")` | `GET /api/v1/analytics/promotions` | Built promotion datasets for recomputation; none for frozen-output reads | Non-causal PRE/DURING/POST summary | `promotion_v1/outputs/promotion_summary.parquet` | Both clients, notebook |

`GET /api/v1/analytics/segments` reads canonical assignments. It is distinct from assigning a new
store with the frozen exploratory model.

## Direct Python

From the repository root:

```powershell
.\.venv\Scripts\python.exe examples\backend_integration.py
```

The example performs:

1. company-shaped CSV → `FileAdapter` → `sales_daily` canonical columns;
2. `ContractRegistry.validate` and domain capability evaluation;
3. frozen forecasting, stockout, segmentation-membership and survival scoring;
4. read-only access to frozen anomaly, basket, promotion and segmentation outputs.

Serving expects task-feature rows, not raw operational tables. External raw data must first satisfy
the canonical contracts and pass the repository's feature/dataset pipeline. The repository currently
exposes that construction as pipeline entrypoints (`pipelines.datasets.build_all`), not as a stable
online transformation API.

## REST

Start the existing API:

```powershell
.\.venv\Scripts\python.exe -m fmcg_sales_intelligence.cli serve --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
.\.venv\Scripts\python.exe examples\rest_api_client.py --base-url http://127.0.0.1:8000
```

`FSI_BASE_URL` can replace `--base-url`. The client calls only routes declared in the current FastAPI
application: health, readiness, two prediction routes, frozen segment assignment, three offline
analytics resources, and the BI summary.

The anomaly and promotion requests deliberately use bounded offsets whose rows contain only finite
JSON numbers. Other pages can currently contain canonical `NaN`/`Infinity` diagnostics that the API
rejects as non-compliant JSON; this is an existing serialization limitation, not hidden by the client.

## External company data

The supported onboarding sequence is:

```text
CSV/Parquet export
  → domain-pack column mapping (`FileAdapter`)
  → canonical contract validation (`ContractRegistry`)
  → capability check (`evaluate_capabilities`)
  → reviewed warehouse/task-dataset pipeline
  → frozen serving or offline analytical workflow
```

Copy `config/domains/_template`, define a declarative mapping, and list only contracts actually
provided by the source system. A `PASS` contract establishes structural compatibility; it does not
prove semantic data quality or make unavailable capabilities valid.

## Notebook

[`fmcg_module_usage.ipynb`](fmcg_module_usage.ipynb) is a compact executable tutorial. It uses the
same interfaces and keeps training, serving and offline analytics explicitly separate.

## Limitations

- Frozen V1 artifacts use synthetic academic data and are not production claims.
- Survival is intentionally offline-only and has no REST endpoint.
- Anomaly, basket and promotion endpoints expose frozen reviewed-format outputs, not online inference.
- Segmentation labels are exploratory pseudo-labels and require human review.
- Raw contract rows cannot be sent directly to model prediction routes; task feature construction is required.
- Some offline analytical pages contain non-finite diagnostic values and cannot currently be serialized by FastAPI.
