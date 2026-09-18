# Local-demo security boundary V1

## Implemented local-demo controls

- CORS is restricted to configurable local origins; wildcard origins are not enabled.
- POST/PUT/PATCH bodies have a configurable two-megabyte ceiling and oversized input returns 413.
- Prediction and contract-validation batches remain capped at 1,000 rows; analytics pagination is capped at 500.
- Pydantic rejects unknown fields, malformed values, invalid date intervals and oversized filter lists.
- Analytical SQL uses bound parameters; only breakdown columns from a fixed allowlist enter SQL text.
- Responses receive request IDs, `nosniff`, same-origin framing and no-referrer headers.
- Validation and internal errors use structured envelopes without tracebacks, filesystem roots, credentials or environment dumps.
- Canonical model loading is limited to trusted DVC-owned server artifacts. No API accepts client paths, pickle/joblib payloads, CSV, or Parquet uploads.
- `.env`, DVC cache/auth state, raw data, model artifacts, MLflow state, frontend build output and `node_modules` are excluded from Git.

## Deferred production controls

Authentication, authorization, TLS termination, distributed rate limiting, a secrets manager, WAF, centralized audit logs and multi-instance quotas are not implemented. A per-process limiter would provide misleading protection under multiple workers, so rate limiting is explicitly deferred. The system is `LOCAL_TRUSTED_ENVIRONMENT_ONLY`, not internet-production ready. Vite variables are public configuration and must never contain secrets.
