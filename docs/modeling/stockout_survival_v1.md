# Stockout Survival V1

Stockout Survival V1 estimates time from an inventory snapshot `t` to the first future physical stockout onset. It is distinct from Classification V1: an origin without an observed event is right-censored rather than assigned a negative class.

The primary risk set requires `available_quantity > 0` and positive observable follow-up. Origins already inside a zero-inventory episode and last-day origins with no future observation are excluded. For observed events, duration is `event_time_days`; otherwise duration is `censor_time_days`. Follow-up is administratively censored at seven days or earlier at dataset end. The physical episode ID reuses the validated warehouse–SKU zero-run definition.

Repeated daily origins from one warehouse–SKU, including several origins pointing to one physical event, are not independent subjects. V1 uses chronological landmark cohorts, a seven-day outcome-window embargo and physical-event boundary purge. It is not a recurrent-event or time-varying Cox design.

Kaplan–Meier is the descriptive cohort baseline. Predictive V1 uses an L2-penalized Cox proportional hazards model selected from the predeclared penalizers in `configs/modeling/stockout_survival.yaml` by validation Harrell C-index. Higher model partial hazard means shorter expected event-free time; the C-index implementation therefore negates risk for lifelines' predicted-time orientation.

The model uses a reduced, predeclared point-in-time feature set to avoid exact inventory identities and unstable derived-variable collinearity. Schoenfeld-residual diagnostics are reported but their p-values are descriptive because repeated origins violate classical independence. Hazard ratios are associations conditional on the model, not causal effects.

Run with `python -m src.modeling.cli run --task stockout_survival`. The stable canonical output is DVC-managed at `artifacts/canonical/stockout_survival_v1/`. No DVC remote is configured.
