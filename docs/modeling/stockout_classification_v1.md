# Stockout Classification V1

This experiment predicts whether a warehouse–SKU will have `available_quantity <= 0` within `(t,t+7 days]`, using only the inventory snapshot at `t` and history strictly before `t`. Multiple positive prediction origins may point to one physical zero-inventory run; therefore positive horizon rows are not independent events.

Physical episodes are stable warehouse–SKU zero-inventory runs beginning at a `>0 → <=0` transition and ending at the first later positive snapshot. Each positive horizon maps to the episode containing its `first_stockout_date`. A deterministic boundary purge removes training rows mapped to an episode also represented in the later evaluation block. A seven-day embargo separately prevents overlapping target-information windows.

Allowed features are current inventory/reservations, reorder and safety thresholds, inventory ratios/distances, historical regional sales velocity over `[t-7,t)`, historical replenishment over `[t-7,t)`, and categorical warehouse/SKU IDs. Classification and survival outcomes, future stockout dates, censoring fields and future delivery outcomes are forbidden. The historical replenishment total is observable; actual future delivery realization is not.

V1 compares always-negative, reorder-point, safety-stock and seven-day cover rules with class-weighted logistic regression and weighted histogram gradient boosting. Selection uses validation Average Precision. The decision threshold maximizes validation F1 and is frozen with the selected feature/model configuration before test access. Final evaluation reports probability metrics, frozen-threshold metrics, episode detection, first-warning lead time and false-alert runs.

Run locally with `python -m fmcg_sales_intelligence.science.cli run --task stockout_classification`. DVC uses the stable canonical output `artifacts/canonical/stockout_classification_v1/`. There is no DVC remote, so binary recovery is local-only until a remote is configured and populated.

This is an offline experiment on approximately 90 days of synthetic FMCG data. It does not validate production performance. In particular, currently stocked-out origins remain eligible under the approved occurrence target; episode detection counts only alerts strictly before onset to expose the distinction between row discrimination and useful advance warning.
