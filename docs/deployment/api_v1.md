# API V1

Run: `.venv\Scripts\python -m fmcg_sales_intelligence.cli serve`.

System: `GET /health`, `/ready`, `/version`, `/metrics`.

Metadata: `GET /api/v1/contracts`, `/contracts/{id}`, `/domain-packs`, `/domain-packs/{id}`, `/capabilities`.

Validation: `POST /api/v1/data/validate` with `{"contract_id":"sales_daily","rows":[...]}`. This bounded route validates already-normalized demo rows; it does not persist or train.

Prediction: `POST /api/v1/predict/forecast` and `/predict/stockout` with `{"rows":[{...frozen features...}]}`. Responses declare target, horizon, model version and output semantics.

Analytics: `GET /api/v1/analytics/{segments|anomalies|basket-rules|promotions}?offset=0&limit=100`.

BI: `GET /api/v1/bi/summary`, `/bi/timeseries`, and `/bi/breakdown/{brand|category|region|channel|store}`. Queries are fixed and read-only.

