# ServiceDesk integration verification — 2026-11-16

Base: `989569c`. Implementation uses only a new self-contained example, its
independent backend package, CI configuration and documentation. No file under
`src/fmcg_sales_intelligence/` or `config/modeling/` is changed.

## Executed checks

| Check | Actual result |
|---|---|
| Separate local MLflow/engine/backend HTTP processes | 17 passed, 0 failed, 0 skipped; 112.69 s |
| Clean-volume dedicated Docker deployment | Initialization completed; registry/engine/backend healthy |
| Docker HTTP integration suite | 17 passed, 0 failed; 14.67 s |
| Existing isolated + real canonical serving/usage regression | 52 passed, 0 failed, 0 skipped; 51.91 s |
| Backend image lacks platform, MLflow and sklearn packages | PASS: executed importlib discovery assertions inside backend container |
| Engine cannot see company SQLite; backend cannot see approvals | PASS: executed filesystem assertions inside the separate containers |
| Repeated initializer after registration and negative version-3 test | PASS: still approves only immutable versions 1 and 2 |
| Reusable platform/scientific source and modeling configuration diff | Empty |
| Canonical scientific artifact hash comparison | 134 files unchanged (deployment approval file excluded) |
| Ruff | PASS |
| Initial GitHub run 43838160776 | All lint, isolated, churn Docker and ServiceDesk Docker jobs successful |
| Push run 43838597966 | All four jobs successful |

One Docker test run emitted a cache-directory permission warning because the
non-root test user cannot write to copied source. The verification image now uses
a writable `/tmp` cache; no tests/assertions were disabled or weakened. Existing
scientific/dependency deprecation warnings remain. Final documentation/CI changes
are required to pass their own checks before merge.

## Acceptance criteria

| ID | Execution evidence | Result |
|---|---|---|
| AC-01 | Separately installed backend distribution; container has no platform/MLflow/sklearn; real HTTP tests and separate mounts | PASS |
| AC-02 | Read actual SQLite tickets; modifying workload in a private DB copy changes HTTP prediction and matches the model's computed value | PASS |
| AC-03 | Trained Pipeline versions 1/2 registered in separate native MLflow service; downloaded, signature-checked and used for REST/Python parity | PASS |
| AC-04 | Domain YAML loaded with existing DomainPack/DomainRegistry and injected through existing API factory; platform source diff empty | PASS |
| AC-05 | Missing, extra, null, invalid type/category and future-outcome fields rejected over HTTP; invalid stored priority becomes business 422 | PASS |
| AC-06 | Actual `/tickets/1/risk?version=1` and `version=2` return probability, model URI/version/run ID and matching request IDs | PASS |
| AC-07 | Dedicated one-command Compose build with initially empty volumes; synthetic data generation/training/approval automatic; CI uses clean checkouts | PASS |
| AC-08 | 17 tests use real TCP/HTTP, separate processes/containers and MLflow service; no TestClient or mocked inference transport | PASS |
| AC-09 | 52 existing regression tests including real FMCG bundles passed; existing churn and isolated CI jobs green | PASS |
| AC-10 | Three persistent services, one initializer and optional test job; reuse existing engine/native MLflow, no frontend/Kafka/replacement registry | PASS |

## Observed business output

At the fixed reference **2026-01-15 12:00 UTC**, actual ticket 1 returned:

- version 1: SLA breach probability `0.8781390737963874`;
- version 2: SLA breach probability `0.9199574714967982`.

These are computed synthetic smoke outputs, not accuracy or calibration claims.
Run IDs and request IDs are recorded in `verification_evidence.json` and naturally
change in new registries/requests. Model version and immutable URI remain explicit.

## Boundaries and limitations

The backend's feature extractor reads only ticket snapshot fields, never the
separate future-outcome table. All generated tickets precede their SLA deadline.
Training and runtime use the same extraction function and the existing strict
domain mapping. Re-fitting the deterministic model reproduces logged predictions.

The registry and Pipeline artifacts are trusted operator-controlled code/data.
Only explicitly listed numeric model versions may execute; a real registered
version 3 is deliberately unapproved and rejected. The negative test adds that
registry metadata reference to an existing artifact; it does not train or approve
a third model. No HTTP upload/deserialization surface was introduced.

This demonstration has no real company data, real-world quality evaluation,
probability calibration, public authentication, registry access control inside
the private Docker network, HA or capacity certification. SQLite and fixed
snapshots are deliberate small-demo choices. A live deployment needs a genuine
point-in-time snapshot policy, external authentication and operational controls.
Core/FMCG/churn behavior and historical scientific artifacts are preserved.

## Delivery

Branch: `codex/servicedesk-external-integration`.
[PR #3](https://github.com/Eclipse-XS/FMCG-Sales-Intelligence/pull/3).
This report is captured before merge. Final merge is conditional on green checks
for the exact final head; the PR merge event and final response record the merge
SHA and post-merge main CI status. Machine-readable local evidence is in
`verification_evidence.json`.
