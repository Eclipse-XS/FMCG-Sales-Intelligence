"""Promotion Performance V1: descriptive, non-causal matched-window analysis."""
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "configs/modeling/promotion.yaml"
DEFAULT_DAILY = ROOT / "data/processed/promotion_daily/promotion_daily_v1.parquet"
DEFAULT_EXPOSURE = ROOT / "data/processed/promotion_performance/promotion_performance_v1.parquet"


def _portable_path(path):
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return None


def load_data(config_path=DEFAULT_CONFIG, data_path=DEFAULT_DAILY, exposure_path=DEFAULT_EXPOSURE):
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    daily = pd.read_parquet(data_path)
    exposure = pd.read_parquet(exposure_path)
    daily["calendar_date"] = pd.to_datetime(daily.calendar_date)
    return cfg, daily, exposure


def validate_contract(daily, exposure):
    key = ["promotion_id", "store_id", "sku_id", "calendar_date"]
    if daily.duplicated(key).any() or exposure.duplicated(key[:3]).any():
        raise ValueError("DATA_ISSUE_FOUND: duplicate promotion grain")
    if daily.loc[daily.is_observable, "realized_sales_units"].isna().any():
        raise ValueError("DATA_ISSUE_FOUND: observable realized sales are missing")
    if daily.loc[~daily.is_observable, "realized_sales_units"].notna().any():
        raise ValueError("DATA_ISSUE_FOUND: boundary outcomes were zero-filled")
    if daily.loc[daily.is_observable, "valid_selling_price"].isna().any():
        raise ValueError("DATA_ISSUE_FOUND: observable price coverage is incomplete")
    if daily.promotion_overlap.any():
        # Retention is allowed, but canonical eligibility must exclude overlap.
        bad = exposure[exposure.promotion_overlap & (exposure.eligible_pre_vs_during | exposure.eligible_during_vs_post)]
        if len(bad):
            raise ValueError("DATA_ISSUE_FOUND: overlapping exposures remain eligible")


def _period_metrics(daily):
    keys = ["promotion_id", "store_id", "sku_id"]
    observed = daily[daily.is_observable].copy()
    observed["weighted_price_numerator"] = observed.realized_sales_units * observed.valid_selling_price.astype(float)
    grouped = observed.groupby(keys + ["period"], observed=True).agg(
        observed_days=("calendar_date", "nunique"),
        realized_units=("realized_sales_units", "sum"),
        realized_revenue=("realized_revenue", "sum"),
        requested_units=("requested_demand_units", "sum"),
        lost_units=("lost_sales_units", "sum"),
        inventory_censored_days=("demand_censored_by_inventory", "sum"),
        posted_price=("valid_selling_price", "mean"),
        weighted_price_numerator=("weighted_price_numerator", "sum"),
    ).reset_index()
    grouped["units_per_day"] = grouped.realized_units / grouped.observed_days
    grouped["revenue_per_day"] = grouped.realized_revenue.astype(float) / grouped.observed_days
    grouped["requested_units_per_day"] = grouped.requested_units / grouped.observed_days
    grouped["lost_units_per_day"] = grouped.lost_units / grouped.observed_days
    grouped["inventory_censored_day_rate"] = grouped.inventory_censored_days / grouped.observed_days
    grouped["selling_price"] = np.where(
        grouped.realized_units > 0,
        grouped.weighted_price_numerator / grouped.realized_units,
        grouped.posted_price,
    )
    values = ["observed_days", "realized_units", "realized_revenue", "units_per_day", "revenue_per_day", "requested_units", "requested_units_per_day", "lost_units", "lost_units_per_day", "inventory_censored_days", "inventory_censored_day_rate", "selling_price"]
    wide = grouped.pivot(index=keys, columns="period", values=values)
    wide.columns = [f"{period.lower()}_{metric}" for metric, period in wide.columns]
    return wide.reset_index()


def build_exposure_metrics(cfg, daily, contract):
    keys = ["promotion_id", "store_id", "sku_id"]
    metrics = contract.merge(_period_metrics(daily), on=keys, how="left", validate="one_to_one", suffixes=("_contract", ""))
    numeric_suffixes = ("_realized_units", "_realized_revenue", "_units_per_day", "_revenue_per_day", "_requested_units", "_requested_units_per_day", "_lost_units", "_lost_units_per_day", "_inventory_censored_days", "_inventory_censored_day_rate", "_selling_price", "_observed_days")
    for column in metrics.columns:
        if column.endswith(numeric_suffixes):
            metrics[column] = pd.to_numeric(metrics[column], errors="coerce")
    for period, complete in [("pre", "pre_window_complete"), ("during", "during_window_complete"), ("post", "post_window_complete")]:
        for metric in ["realized_units", "realized_revenue", "units_per_day", "revenue_per_day", "requested_units", "requested_units_per_day", "lost_units", "lost_units_per_day", "inventory_censored_days", "inventory_censored_day_rate", "selling_price"]:
            col = f"{period}_{metric}"
            metrics.loc[~metrics[complete], col] = np.nan
    comparisons = [("during", "pre", "eligible_pre_vs_during"), ("post", "during", "eligible_during_vs_post"), ("post", "pre", "eligible_full_cycle")]
    for after, before, eligibility in comparisons:
        prefix = f"{after}_vs_{before}"
        for measure in ["units", "revenue"]:
            a, b = f"{after}_{measure}_per_day", f"{before}_{measure}_per_day"
            metrics[f"{prefix}_absolute_{measure}_per_day"] = np.where(metrics[eligibility], metrics[a] - metrics[b], np.nan)
            relative = pd.Series(np.nan, index=metrics.index, dtype=float)
            defined = metrics[eligibility] & metrics[b].gt(0)
            relative.loc[defined] = (metrics.loc[defined, a] - metrics.loc[defined, b]) / metrics.loc[defined, b]
            metrics[f"{prefix}_relative_{measure}_change"] = relative
        metrics[f"{prefix}_selling_price_change"] = np.where(metrics[eligibility], metrics[f"{after}_selling_price"] - metrics[f"{before}_selling_price"], np.nan)
    metrics["zero_baseline"] = metrics.eligible_pre_vs_during & metrics.pre_units_per_day.eq(0)
    threshold = float(cfg["low_baseline_units_per_day"])
    metrics["low_baseline"] = metrics.eligible_pre_vs_during & metrics.pre_units_per_day.gt(0) & metrics.pre_units_per_day.lt(threshold)
    metrics["review_status"] = cfg["review_status"]
    metrics["analysis_semantics"] = "DESCRIPTIVE_NON_CAUSAL"
    return metrics


def promotion_summary(exposure):
    rows = []
    for promotion_id, all_rows in exposure.groupby("promotion_id", sort=True):
        row = {"promotion_id": promotion_id, "start_date": all_rows.start_date.min(), "end_date": all_rows.end_date.max(), "duration_days": int(all_rows.duration_days.iloc[0]), "exposure_count": len(all_rows)}
        for flag in ["pre_window_complete", "during_window_complete", "post_window_complete", "eligible_pre_vs_during", "eligible_during_vs_post", "eligible_full_cycle"]:
            row[f"{flag}_count"] = int(all_rows[flag].sum())
        for period, completeness in [("pre", "pre_window_complete"), ("during", "during_window_complete"), ("post", "post_window_complete")]:
            cohort = all_rows[all_rows[completeness]]
            days = cohort[f"{period}_observed_days"].sum()
            units = cohort[f"{period}_realized_units"].sum(min_count=1)
            revenue = cohort[f"{period}_realized_revenue"].astype(float).sum(min_count=1)
            row[f"{period}_realized_units"] = units
            row[f"{period}_units_per_day"] = units / days if days else np.nan
            row[f"{period}_realized_revenue"] = revenue
            row[f"{period}_revenue_per_day"] = revenue / days if days else np.nan
            sold = cohort[f"{period}_realized_units"].sum()
            row[f"{period}_selling_price"] = revenue / sold if sold > 0 else cohort[f"{period}_selling_price"].mean()
        for after, before, eligibility in [("during", "pre", "eligible_pre_vs_during"), ("post", "during", "eligible_during_vs_post"), ("post", "pre", "eligible_full_cycle")]:
            cohort = all_rows[all_rows[eligibility]]
            prefix = f"{after}_vs_{before}"
            for measure in ["units", "revenue"]:
                vals = cohort[f"{prefix}_absolute_{measure}_per_day"]
                row[f"{prefix}_absolute_{measure}_per_day"] = all_rows.loc[all_rows[eligibility], f"{after}_{measure}_per_day"].sum() - all_rows.loc[all_rows[eligibility], f"{before}_{measure}_per_day"].sum() if len(cohort) else np.nan
                baseline = all_rows.loc[all_rows[eligibility], f"{before}_{measure}_per_day"].sum()
                row[f"{prefix}_relative_{measure}_change"] = row[f"{prefix}_absolute_{measure}_per_day"] / baseline if baseline > 0 else np.nan
            row[f"{prefix}_median_exposure_units_change"] = vals.median() if len(cohort) else np.nan
            row[f"{prefix}_positive_share"] = (vals > 0).mean() if len(cohort) else np.nan
            row[f"{prefix}_negative_share"] = (vals < 0).mean() if len(cohort) else np.nan
            row[f"{prefix}_zero_share"] = (vals == 0).mean() if len(cohort) else np.nan
        row["zero_baseline_count"] = int(all_rows.zero_baseline.sum())
        row["low_baseline_count"] = int(all_rows.low_baseline.sum())
        row["inventory_censored_day_rate"] = all_rows.during_inventory_censored_days.sum() / all_rows.during_observed_days.sum()
        row["review_status"] = "UNREVIEWED"
        row["analysis_semantics"] = "DESCRIPTIVE_NON_CAUSAL"
        rows.append(row)
    return pd.DataFrame(rows)


def sensitivity(daily, exposure, days=14):
    keys = ["promotion_id", "store_id", "sku_id"]
    pre = daily[(daily.period == "PRE") & daily.is_observable].copy()
    pre = pre[pre.calendar_date >= pre.promotion_start_date - pd.to_timedelta(days, unit="D")]
    alt = pre.groupby(keys).agg(alt_pre_days=("calendar_date", "nunique"), alt_pre_units=("realized_sales_units", "sum")).reset_index()
    x = exposure[exposure.eligible_pre_vs_during].merge(alt, on=keys, how="left")
    x["alternative_pre_units_per_day"] = x.alt_pre_units / x.alt_pre_days
    x["alternative_change"] = x.during_units_per_day - x.alternative_pre_units_per_day
    x["canonical_change"] = x.during_vs_pre_absolute_units_per_day
    x["sign_agreement"] = np.sign(x.alternative_change) == np.sign(x.canonical_change)
    x["magnitude_difference"] = (x.alternative_change - x.canonical_change).abs()
    return x[keys + ["canonical_change", "alternative_change", "sign_agreement", "magnitude_difference"]]


def run_promotion_experiment(config_path=DEFAULT_CONFIG, data_path=DEFAULT_DAILY, exposure_path=DEFAULT_EXPOSURE, output_dir=None, experiment_id=None, overwrite=False):
    cfg, daily, contract = load_data(config_path, data_path, exposure_path)
    validate_contract(daily, contract)
    exposure = build_exposure_metrics(cfg, daily, contract)
    summary = promotion_summary(exposure)
    sens = sensitivity(daily, exposure, int(cfg["sensitivity_pre_days"][0]))
    out = Path(output_dir or ROOT / "artifacts/experiments/promotion" / (experiment_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")))
    shutil.rmtree(out, ignore_errors=overwrite)
    if out.exists():
        raise FileExistsError(out)
    for directory in [out / "outputs", out / "diagnostics", out / "figures"]:
        directory.mkdir(parents=True, exist_ok=True)
    exposure.to_parquet(out / "outputs/exposure_metrics.parquet", index=False)
    summary.to_parquet(out / "outputs/promotion_summary.parquet", index=False)
    review = summary[["promotion_id", "start_date", "end_date", "eligible_pre_vs_during_count", "during_vs_pre_absolute_units_per_day", "during_vs_pre_relative_units_change", "review_status", "analysis_semantics"]]
    review.to_csv(out / "outputs/review_promotions.csv", index=False)
    sens.to_csv(out / "diagnostics/baseline_sensitivity.csv", index=False)
    weekday = daily.assign(weekday=daily.calendar_date.dt.day_name()).groupby(["promotion_id", "period", "weekday"]).size().rename("exposure_days").reset_index()
    weekday.to_csv(out / "diagnostics/weekday_composition.csv", index=False)
    inventory = exposure.groupby("promotion_id").agg(censored_days=("during_inventory_censored_days", "sum"), observed_days=("during_observed_days", "sum"), exposures_with_censoring=("during_inventory_censored_days", lambda x: int((x > 0).sum()))).reset_index()
    inventory["censored_day_rate"] = inventory.censored_days / inventory.observed_days
    inventory.to_csv(out / "diagnostics/inventory_context.csv", index=False)
    extreme = exposure[exposure.eligible_pre_vs_during].sort_values("during_vs_pre_relative_units_change", key=lambda s: s.abs(), ascending=False).head(50)
    extreme.to_csv(out / "diagnostics/extreme_change_diagnostics.csv", index=False)
    slice_rows = []
    for dimension in ["brand_name", "category_name", "region_id", "store_type", "channel", "sku_id"]:
        for value, group in exposure[exposure.eligible_pre_vs_during].groupby(dimension, dropna=False):
            pre, during = group.pre_units_per_day.sum(), group.during_units_per_day.sum()
            slice_rows.append({"dimension": dimension, "value": str(value), "eligible_exposures": len(group), "pre_units_per_day": pre, "during_units_per_day": during, "absolute_units_change_per_day": during-pre, "relative_units_change": (during-pre)/pre if pre>0 else np.nan, "median_exposure_change": group.during_vs_pre_absolute_units_per_day.median(), "inventory_censored_day_rate": group.during_inventory_censored_days.sum()/group.during_observed_days.sum()})
    slices = pd.DataFrame(slice_rows)
    slices.to_parquet(out / "outputs/slice_metrics.parquet", index=False)
    differences = []
    for row in summary.itertuples():
        cohort = exposure[(exposure.promotion_id == row.promotion_id) & exposure.eligible_pre_vs_during]
        if len(cohort):
            reconstructed = cohort.during_units_per_day.sum() - cohort.pre_units_per_day.sum()
            differences.append(abs(reconstructed - row.during_vs_pre_absolute_units_per_day))
    max_difference = float(max(differences, default=0.0))
    reconciliation = {"promotion_rows": len(summary), "exposure_rows": len(exposure), "compared_promotions": len(differences), "max_units_difference": max_difference, "passed": bool(max_difference < 1e-12), "policy": cfg["aggregation_policy"]}
    (out / "diagnostics/aggregation_reconciliation.json").write_text(json.dumps(reconciliation, indent=2))
    diag = {"daily_rows": len(daily), "observable_rows": int(daily.is_observable.sum()), "boundary_rows": int((~daily.is_observable).sum()), "zero_sales_rows": int((daily.is_observable & daily.realized_sales_units.eq(0)).sum()), "positive_sales_rows": int((daily.is_observable & daily.realized_sales_units.gt(0)).sum()), "promotion_count": int(daily.promotion_id.nunique()), "exposure_count": len(exposure), "duplicate_daily_keys": int(daily.duplicated(["promotion_id","store_id","sku_id","calendar_date"]).sum()), "overlap_days": int(daily.promotion_overlap.sum()), "date_range": [str(daily.loc[daily.is_observable,"calendar_date"].min().date()), str(daily.loc[daily.is_observable,"calendar_date"].max().date())]}
    (out / "diagnostics/data_diagnostics.json").write_text(json.dumps(diag, indent=2))
    funnel = {k: int(exposure[k].sum()) for k in ["pre_window_complete", "during_window_complete", "post_window_complete", "eligible_pre_vs_during", "eligible_during_vs_post", "eligible_full_cycle"]}
    (out / "diagnostics/eligibility_funnel.json").write_text(json.dumps(funnel, indent=2))
    eligible = exposure[exposure.eligible_pre_vs_during]
    pre, during = eligible.pre_units_per_day.sum(), eligible.during_units_per_day.sum()
    metrics = {"promotion_count": len(summary), "exposure_count": len(exposure), "pre_vs_during_eligible_exposures": int(exposure.eligible_pre_vs_during.sum()), "during_vs_post_eligible_exposures": int(exposure.eligible_during_vs_post.sum()), "full_cycle_eligible_exposures": int(exposure.eligible_full_cycle.sum()), "zero_baseline_exposures": int(exposure.zero_baseline.sum()), "low_baseline_exposures": int(exposure.low_baseline.sum()), "aggregate_pre_units_per_day": pre, "aggregate_during_units_per_day": during, "aggregate_descriptive_units_change_per_day": during-pre, "aggregate_descriptive_units_change_fraction": (during-pre)/pre if pre else None, "median_exposure_units_change_per_day": eligible.during_vs_pre_absolute_units_per_day.median(), "positive_exposure_share": float((eligible.during_vs_pre_absolute_units_per_day>0).mean()), "negative_exposure_share": float((eligible.during_vs_pre_absolute_units_per_day<0).mean()), "aggregate_revenue_change_per_day": float(eligible.during_revenue_per_day.sum()-eligible.pre_revenue_per_day.sum()), "inventory_censored_day_rate": float(eligible.during_inventory_censored_days.sum()/eligible.during_observed_days.sum()), "baseline_sign_stability": float(sens.sign_agreement.mean()), "readiness": "READY_WITH_LIMITATIONS"}
    for name in ["metrics.json", "dvc_metrics.json"]:
        (out / name).write_text(json.dumps(metrics, indent=2))
    selected = {"task_type":"DESCRIPTIVE_PROMOTION_ANALYSIS","primary_outcome":"realized_sales_units","baseline":cfg["canonical_baseline"],"window_policy":cfg["window_policy"],"aggregation_policy":cfg["aggregation_policy"],"zero_baseline_policy":cfg["relative_change_policy"],"low_baseline_units_per_day":cfg["low_baseline_units_per_day"],"overlap_policy":cfg["overlap_policy"],"eligibility_policy":cfg["eligibility_policy"],"sensitivity_pre_days":cfg["sensitivity_pre_days"],"context_semantics":{"requested_demand":"SYNTHETIC_REQUESTED_DEMAND_CONTEXT","lost_sales":"SYNTHETIC_LOST_SALES_CONTEXT"},"daily_dataset_fingerprint":_sha(data_path),"exposure_dataset_fingerprint":_sha(exposure_path)}
    (out / "selected_method.json").write_text(json.dumps(selected, indent=2))
    (out / "resolved_config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    summary.set_index("promotion_id")[["pre_units_per_day","during_units_per_day","post_units_per_day"]].plot.bar(figsize=(8,4)); plt.ylabel("Realized units / observed day"); plt.tight_layout(); plt.savefig(out/"figures/units_before_during_after.png",dpi=180); plt.close()
    summary.set_index("promotion_id")[["pre_revenue_per_day","during_revenue_per_day","post_revenue_per_day"]].plot.bar(figsize=(8,4)); plt.ylabel("Realized revenue / observed day"); plt.tight_layout(); plt.savefig(out/"figures/revenue_before_during_after.png",dpi=180); plt.close()
    eligible.during_vs_pre_absolute_units_per_day.hist(bins=30,figsize=(7,4)); plt.xlabel("During-vs-PRE units/day difference"); plt.tight_layout(); plt.savefig(out/"figures/exposure_change_distribution.png",dpi=180); plt.close()
    plt.scatter(eligible.during_vs_pre_selling_price_change,eligible.during_vs_pre_absolute_units_per_day,s=8,alpha=.4); plt.xlabel("Selling-price difference"); plt.ylabel("Units/day difference"); plt.tight_layout(); plt.savefig(out/"figures/price_vs_units_change.png",dpi=180); plt.close()
    inventory.set_index("promotion_id").censored_day_rate.plot.bar(figsize=(7,4)); plt.ylabel("Inventory-censored day rate"); plt.tight_layout(); plt.savefig(out/"figures/inventory_context.png",dpi=180); plt.close()
    report = f"""# Promotion Performance V1\n\n## 1–9. Objective, scope, contract, windows, eligibility and baseline\nThis is a descriptive, non-causal comparison of observed realized sales. The validated complete daily grid distinguishes observed zero from an unobservable boundary. Matched-duration PRE is canonical; relative change is null for zero baselines and `{cfg['low_baseline_units_per_day']}` units/day is a diagnostic threshold, not an exclusion.\n\n## 10–17. Promotion results, heterogeneity, units, revenue, price, full cycle and inventory\n{summary.to_markdown(index=False)}\n\nAggregate measures reconstruct underlying eligible exposure totals. Volume-weighted promotion results and exposure medians are separate. Price is units-weighted when units are positive, otherwise mean valid posted price. Inventory censoring is contextual and is not used for causal correction.\n\n## 18–21. Synthetic context, business slices, calendar and sensitivity\nRequested and lost demand are explicitly synthetic context. Detailed SKU, brand, category, region, store-type and channel slices are persisted. Weekday composition is diagnostic only. The predeclared 14-day PRE sensitivity has sign stability {metrics['baseline_sign_stability']:.1%}; it does not replace the matched-duration baseline.\n\n## 22–26. Review, readiness, limitations, reproducibility and future hypotheses\nAll promotions remain UNREVIEWED. Readiness is READY_WITH_LIMITATIONS: only three synthetic promotions, 90 days, one complete full-cycle promotion, no causal identification, and no external validation. DVC stage `promotion_v1` persists the analysis. Future hypotheses require business review and a separately designed causal study.\n"""
    (out / "report.md").write_text(report, encoding="utf-8")
    manifest = {"experiment_id":experiment_id or out.name,"task":"promotion_performance","status":"complete","created_at":datetime.now(timezone.utc).isoformat(),"daily_dataset_path":_portable_path(data_path),"daily_dataset_fingerprint":_sha(data_path),"exposure_dataset_path":_portable_path(exposure_path),"exposure_dataset_fingerprint":_sha(exposure_path),"grain":["promotion_id","store_id","sku_id"],"date_range":diag["date_range"],"promotion_count":len(summary),"exposure_count":len(exposure),"window_contract":cfg["window_policy"],"eligibility_contract":cfg["eligibility_policy"],"overlap_policy":cfg["overlap_policy"],"primary_outcomes":["realized_sales_units","realized_revenue"],"context_outcomes":["requested_demand_units","lost_sales_units","demand_censored_by_inventory"],"price_semantic":"STORE_SKU_DATE_VALIDITY_INTERVAL","revenue_semantic":"realized_sales_units_x_valid_selling_price","profit_availability":"UNAVAILABLE","roi_availability":"UNAVAILABLE","baseline":cfg["canonical_baseline"],"zero_baseline_policy":cfg["relative_change_policy"],"aggregation_policy":cfg["aggregation_policy"],"sensitivity_policy":cfg["sensitivity_pre_days"],"git":{"commit":_git("rev-parse","HEAD"),"branch":_git("branch","--show-current"),"dirty":bool(_git("status","--porcelain"))},"dvc":{"stage":"promotion_v1","remote":None},"readiness":"READY_WITH_LIMITATIONS","library_versions":{"python":platform.python_version(),"pandas":pd.__version__},"artifacts":{"summary":"outputs/promotion_summary.parquet","exposures":"outputs/exposure_metrics.parquet","slices":"outputs/slice_metrics.parquet","review":"outputs/review_promotions.csv"}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    return {"experiment_id":manifest["experiment_id"],"output_dir":str(out),"selected_model":"descriptive_promotion_analysis","test_metrics":metrics}
