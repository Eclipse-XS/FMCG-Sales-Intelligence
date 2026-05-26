# Backend V1

FastAPI routers call service/domain code; transformation and prediction logic is not embedded in transport handlers. `/api/v1` exposes contracts, domain packs, capability discovery, bounded normalized-row validation, frozen predictions, caveated offline analytics, and fixed BI aggregates. OpenAPI is generated from typed request boundaries.

Errors use a request ID and safe message without tracebacks or configuration disclosure. CORS is restricted to configured local origins. No arbitrary SQL, arbitrary filesystem path, uploaded pickle/joblib, or online `/train` endpoint exists.

