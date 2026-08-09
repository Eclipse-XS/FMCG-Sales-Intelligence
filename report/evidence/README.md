# Reproducible Report Evidence

Generated exclusively from materialized canonical artifacts and processed-dataset metadata. The generator does not train models, write canonical artifacts, or modify DVC state.

## Reproduce

```powershell
.\.venv\Scripts\python.exe scripts\generate_report_evidence.py
```

Use `--skip-tests` only for a faster local refresh; that mode explicitly marks testing evidence as not regenerated.

## Methodological boundaries

- Classification curves are derived from frozen out-of-sample labels and probabilities, without model inference.
- PCA is used only for two-dimensional visualization of frozen cluster assignments.
- Anomalies are review candidates, not confirmed errors, fraud, or events.
- Basket rules are associations, not causal relations or recommendations.
- Promotion results are descriptive observed comparisons, not causal effects, incrementality, or ROI.
- Every PNG figure has a matching SVG. Traceability and limitations are recorded in `summary/evidence_manifest.json`.

## Unsupported evidence

No requested evidence was omitted.
