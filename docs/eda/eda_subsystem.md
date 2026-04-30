# Reusable EDA subsystem

EDA in this project has three distinct roles. Development-time scientific EDA investigates task semantics and modeling feasibility. Reusable profiling recomputes structured evidence whenever a Parquet artifact changes. Future production monitoring may schedule these runs and compare them, but an EDA comparison is not a formal drift detector and makes no statistical process-control claim.

## Architecture and API

`EDAService.run(EDARequest(...))` is the stable application boundary. Task analyzers and generic profiling produce an `EDAResult`; Markdown, JSON, figures, CLI and a future FastAPI adapter consume that object. HTTP code must call the service directly and serialize `result.to_dict()`; it must not invoke a subprocess or parse Markdown.

```python
from src.eda import run_eda

result = run_eda(task="forecasting")
payload = result.to_dict()
```

Errors such as unknown tasks, missing files, missing required columns and incompatible comparisons are domain-specific exceptions. Failed analysis is not persisted as a completed run.

## CLI

```text
python -m src.eda.cli run --task all
python -m src.eda.cli run --task forecasting
python -m src.eda.cli run --task stockout
python -m src.eda.cli run --task forecasting --dataset path/to/forecasting.parquet
python -m src.eda.cli list-runs
python -m src.eda.cli show-run RUN_ID
python -m src.eda.cli latest --task forecasting
python -m src.eda.cli compare RUN_A RUN_B
python -m src.eda.run_all
```

## Run format and identity

Canonical history is stored under `reports/eda/runs/<run_id>/` with `manifest.json`, `metrics.json`, `findings.json`, `report.md`, and `figures/`. `reports/eda/latest.json` is a Windows-safe pointer. Input data is never copied. Each identity records file SHA-256, schema SHA-256, byte size, row count and schema. Run IDs combine a UTC timestamp, data fingerprint prefix and random suffix, preventing collisions.

The manifest contains task, status, inputs, profiles, metrics, structured findings, readiness and artifact references. Project-local paths are persisted relative to the repository. Explicit external input paths remain external paths because rewriting them would destroy provenance.

## Profiling and readiness

The generic profile covers schema, missingness, cardinality, numeric summaries, categorical frequencies, dates and duplicates. Task analyzers retain task-specific evidence. Findings use `INFO`, `WARNING`, and `CRITICAL`; readiness uses `READY`, `READY_WITH_LIMITATIONS`, `NOT_READY`, and `NOT_APPLICABLE`.

Forecast target coverage thresholds are centralized: below 50% is not ready, 50–80% is ready with limitations, and higher coverage can still be limited by history length. Fewer than 30 independent stockout episodes is not ready. These are transparent screening rules, not proof of model quality. Scientific limitations can keep a dataset at `READY_WITH_LIMITATIONS` even when numeric thresholds pass.

## Comparison

Compatible runs must share an analysis type. Comparison reports identical/non-identical fingerprints, added/removed columns, dtype changes and numeric metric deltas. It deliberately calls these profile changes, not data drift. Formal drift monitoring requires a separately defined reference policy, sampling plan, statistical thresholds and operational response process.
