from pathlib import Path

import numpy as np
import pandas as pd

from fmcg_sales_intelligence.science import run_experiment
from fmcg_sales_intelligence.science.promotion import build_exposure_metrics, load_data, promotion_summary, sensitivity, validate_contract


def prepared():
    cfg, daily, contract = load_data()
    validate_contract(daily, contract)
    return cfg, daily, contract, build_exposure_metrics(cfg, daily, contract)


def test_corrected_contract_zero_boundary_and_semantics():
    cfg, daily, contract, exposure = prepared()
    assert len(daily) == 259200 and not daily.duplicated(["promotion_id","store_id","sku_id","calendar_date"]).any()
    assert daily.loc[daily.is_observable, "realized_sales_units"].notna().all()
    assert (daily.loc[daily.is_observable & daily.realized_sales_units.eq(0), "realized_sales_units"] == 0).all()
    assert daily.loc[~daily.is_observable, "realized_sales_units"].isna().all()
    assert set(daily.requested_demand_semantics) == {"SYNTHETIC_REQUESTED_DEMAND_CONTEXT"}
    assert set(daily.lost_sales_semantics) == {"SYNTHETIC_LOST_SALES_CONTEXT"}


def test_eligibility_overlap_and_primary_outcome():
    cfg, daily, contract, exposure = prepared()
    assert exposure.eligible_pre_vs_during.sum() == 1920
    assert exposure.eligible_during_vs_post.sum() == 1920
    assert exposure.eligible_full_cycle.sum() == 960
    assert not exposure.loc[exposure.promotion_overlap, "eligible_pre_vs_during"].any()
    assert cfg["primary_outcome"] == "realized_sales_units"


def test_daily_formulas_changes_zero_and_low_baseline():
    cfg, daily, contract, x = prepared()
    eligible = x[x.eligible_pre_vs_during]
    assert np.allclose(eligible.pre_units_per_day, eligible.pre_realized_units / eligible.pre_observed_days)
    assert np.allclose(eligible.pre_revenue_per_day, eligible.pre_realized_revenue.astype(float) / eligible.pre_observed_days)
    assert np.allclose(eligible.during_vs_pre_absolute_units_per_day, eligible.during_units_per_day - eligible.pre_units_per_day)
    defined = eligible.pre_units_per_day > 0
    expected = (eligible.loc[defined,"during_units_per_day"]-eligible.loc[defined,"pre_units_per_day"])/eligible.loc[defined,"pre_units_per_day"]
    assert np.allclose(eligible.loc[defined,"during_vs_pre_relative_units_change"], expected)
    assert eligible.loc[eligible.zero_baseline,"during_vs_pre_relative_units_change"].isna().all()
    assert (eligible.loc[eligible.low_baseline,"pre_units_per_day"] < cfg["low_baseline_units_per_day"]).all()


def test_revenue_price_profit_roi_and_full_cycle():
    cfg, daily, contract, x = prepared()
    eligible = x[x.eligible_pre_vs_during]
    assert np.allclose(eligible.during_vs_pre_absolute_revenue_per_day, eligible.during_revenue_per_day-eligible.pre_revenue_per_day)
    assert eligible.during_selling_price.notna().all()
    assert not {"profit","roi","causal_uplift","ate"} & set(x.columns)
    full = x[x.eligible_full_cycle]
    assert full.post_vs_pre_absolute_units_per_day.notna().all()


def test_aggregate_is_reconstructed_not_mean_percentage():
    cfg, daily, contract, x = prepared()
    summary = promotion_summary(x)
    for row in summary.itertuples():
        cohort = x[(x.promotion_id == row.promotion_id) & x.eligible_pre_vs_during]
        if len(cohort):
            aggregate = (cohort.during_units_per_day.sum()-cohort.pre_units_per_day.sum())/cohort.pre_units_per_day.sum()
            assert np.isclose(row.during_vs_pre_relative_units_change, aggregate)
    assert {"during_vs_pre_positive_share","during_vs_pre_negative_share","during_vs_pre_zero_share"}.issubset(summary.columns)


def test_sensitivity_weekday_inventory_and_review(tmp_path):
    cfg, daily, contract, x = prepared()
    s = sensitivity(daily, x, 14)
    assert len(s) == x.eligible_pre_vs_during.sum() and s.sign_agreement.notna().all()
    assert cfg["canonical_baseline"] == "MATCHED_DURATION_PRE"
    result = run_experiment("promotion", output_dir=tmp_path/"promotion", experiment_id="test", overwrite=True)
    out = Path(result["output_dir"])
    review = pd.read_csv(out/"outputs/review_promotions.csv")
    assert set(review.review_status) == {"UNREVIEWED"}
    assert set(review.analysis_semantics) == {"DESCRIPTIVE_NON_CAUSAL"}
    assert (out/"diagnostics/weekday_composition.csv").exists()
    assert (out/"diagnostics/inventory_context.csv").exists()
    assert not {"accuracy","precision","recall","f1","roc_auc","ate","roi"} & set(result["test_metrics"])


def test_deterministic_outputs_and_artifact_schema(tmp_path):
    a = run_experiment("promotion", output_dir=tmp_path/"a", experiment_id="a", overwrite=True)
    b = run_experiment("promotion", output_dir=tmp_path/"b", experiment_id="b", overwrite=True)
    ea = pd.read_parquet(Path(a["output_dir"])/"outputs/exposure_metrics.parquet")
    eb = pd.read_parquet(Path(b["output_dir"])/"outputs/exposure_metrics.parquet")
    pd.testing.assert_frame_equal(ea, eb)
    assert {"promotion_id","store_id","sku_id","review_status","analysis_semantics"}.issubset(ea.columns)
