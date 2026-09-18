# Promotion Data Contract Refinement V1

The original promotion mart aggregated a sparse positive-sales fact. This made an observable all-zero window indistinguishable from a period outside the dataset boundary. Promotion Performance Modeling V1 was blocked.

The corrected source of truth is `mart_promotion_daily`, at `promotion_id × store_id × sku_id × calendar_date`. It uses the complete `fact_daily_demand` grid. Observable missing positive facts become numeric zero; dates outside 2024-01-01–2024-03-30 remain unobservable with null outcomes and explicit boundary status.

Windows use matched promotion duration D: PRE `[start-D,start)`, DURING `[start,end]`, POST `(end,end+D]`. Expected and observed calendar-day counts determine completeness and analysis-specific eligibility. Ambiguous overlapping DURING exposure-days are retained but excluded from canonical comparisons.

Primary outcome is realized sales. Requested demand and lost sales are explicitly synthetic context; inventory censoring is carried as daily flags plus period counts and rates. Daily price is joined by the store-SKU validity interval effective on each calendar date; realized revenue is realized units multiplied by that valid selling price. Profit and ROI are excluded from the canonical contract.

The exposure mart is built only after the daily grid. Complete zero-sales windows aggregate to zero. Incomplete boundary windows retain partial audit totals but canonical comparison totals remain null.
