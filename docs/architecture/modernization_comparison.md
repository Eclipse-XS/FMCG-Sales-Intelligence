# Before and after

| Concern | Before | After |
|---|---|---|
| Serving boundary | Fixed FMCG model names in Python registry | Independent injected Engine; native MLflow versions or process-local models |
| Feature compatibility | Union of batch keys; missing per-row cells could pass | Per-row keys, exact named schema, explicit coercion/null/category/finite rules |
| Domain integration | FMCG column rename files | Injected typed DomainPack, declarative mapping/scaling, reviewed Python transformations |
| Preprocessing | Task-specific serving code | Fitted Pipeline for BYOM; existing canonical preprocessing retained in FMCG bridge |
| Registration | Two canonical joblib artifacts | Operator API for compatible Pipelines; MLflow owns persistent signatures/versions |
| Trust | Implicit local deserialization | Immutable MLflow approvals or operator SHA-256 local approval; no request uploads |
| Interfaces | Task-coupled routes | Shared Engine used by versioned REST and Python; legacy routes remain |
| Testing | Unit suite depends on hidden data/models | Isolated trained fixtures; unchanged canonical assertions in separate suite |
| Demo | Private/generated artifacts assumed | Two deterministic synthetic Pipelines, generated inputs and REST/Python parity |
| Operations | Anonymous Grafana Admin and default passwords | Anonymous disabled, explicit secrets, loopback ports, separate one-service demo |
| Kafka | Replay easily confused with inference | Explicit experimental ingestion-only extension, excluded from core demo |
| Science | Seven specialized workflows | Same seven implementations, configurations, embargoes and results retained |

The engine does not unify training, rule mining and online prediction. Existing
science CLI functions retain their distinct batch semantics. The scope adds an
integration boundary around execution, not a replacement scientific framework.
