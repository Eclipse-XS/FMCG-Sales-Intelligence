"""Regression tests for Promotion Data Contract V1."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D = pd.read_parquet(ROOT / "data/processed/promotion_daily/promotion_daily_v1.parquet")
P = pd.read_parquet(ROOT / "data/processed/promotion_performance/promotion_performance_v1.parquet")


def test_daily_and_exposure_grains_unique():
    assert len(D) == 259200
    assert not D.duplicated(["promotion_id", "store_id", "sku_id", "calendar_date"]).any()
    assert len(P) == 2880
    assert not P.duplicated(["promotion_id", "store_id", "sku_id"]).any()


def test_matched_period_classification_and_expected_days():
    assert set(D.period) == {"PRE", "DURING", "POST"}
    assert (P[["pre_expected_days", "during_expected_days", "post_expected_days"]] == 30).all().all()
    assert (D.loc[D.period == "PRE", "calendar_date"] < D.loc[D.period == "PRE", "promotion_start_date"]).all()
    assert (D.loc[D.period == "POST", "calendar_date"] > D.loc[D.period == "POST", "promotion_end_date"]).all()


def test_observed_zero_distinct_from_boundary_null():
    observed_zero = D[D.is_observable & D.realized_sales_units.eq(0)]
    unobservable = D[~D.is_observable]
    assert len(observed_zero) == 119848
    assert observed_zero.realized_sales_units.notna().all()
    assert unobservable.realized_sales_units.isna().all()


def test_zero_window_complete_and_boundary_incomplete():
    assert (P.pre_window_complete & P.pre_realized_units.eq(0)).any()
    assert P.loc[P.promotion_id.eq(1), "pre_window_complete"].eq(False).all()
    assert P.loc[P.promotion_id.eq(1), "pre_realized_units"].isna().all()


def test_completeness_and_eligibility():
    assert P.pre_window_complete.sum() == 1920
    assert P.during_window_complete.sum() == 2880
    assert P.post_window_complete.sum() == 1920
    assert P.eligible_pre_vs_during.sum() == 1920
    assert P.eligible_during_vs_post.sum() == 1920
    assert P.eligible_full_cycle.sum() == 960


def test_overlap_price_revenue_and_context():
    assert not D.promotion_overlap.any()
    assert D.loc[D.is_observable, "valid_selling_price"].notna().all()
    observed = D[D.is_observable]
    revenue = observed.realized_revenue.astype(float)
    price = observed.valid_selling_price.astype(float)
    delta = revenue - observed.realized_sales_units * price
    assert delta.abs().max() < 1e-9
    assert set(D.requested_demand_semantics) == {"SYNTHETIC_REQUESTED_DEMAND_CONTEXT"}
    assert set(D.lost_sales_semantics) == {"SYNTHETIC_LOST_SALES_CONTEXT"}


def test_no_fake_profit_or_roi():
    assert not {"promo_profit", "profit", "roi"} & set(P.columns)
