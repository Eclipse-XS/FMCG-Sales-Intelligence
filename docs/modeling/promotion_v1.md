# Promotion Performance V1

Promotion Performance V1 is a descriptive, non-causal analytical stage. Its primary question is how observed realized sales during a promotion differed from the same exposure's matched-duration PRE period.

The analysis consumes the corrected complete daily promotion grid. Observable zero sales remain numeric zero; dates outside the source boundary remain unavailable. PRE, DURING and POST use matched promotion duration. PRE-vs-DURING, DURING-vs-POST and full-cycle comparisons use their separate frozen eligibility flags.

Realized units and derived realized revenue are primary outcomes. Requested demand and lost sales remain explicitly synthetic context. Inventory censoring is contextual. Selling price is units-weighted when units are positive; otherwise the mean valid posted price is reported. Profit and ROI are unsupported.

Matched-duration PRE is canonical. Relative change is null when PRE units/day is zero. A predeclared threshold of 0.5 units/day marks unstable low baselines without excluding them. A 14-day immediate PRE sensitivity is diagnostic and cannot replace the canonical baseline.

Promotion summaries reconstruct underlying eligible exposure totals; they do not average exposure percentages. Exposure distributions and business slices are reported separately. All review rows remain `UNREVIEWED`, and all semantics remain `DESCRIPTIVE_NON_CAUSAL`.

Limitations include synthetic data, 90 days, three physical promotions, one full-cycle promotion, calendar and trend confounding, inventory constraints, and no causal identification or external validation.

Reproduce with:

```powershell
.\.venv\Scripts\dvc.exe repro promotion_v1
```
