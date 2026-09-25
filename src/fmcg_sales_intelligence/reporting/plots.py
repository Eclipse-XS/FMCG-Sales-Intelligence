"""Publication-oriented plots for the frozen evidence package."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import precision_recall_curve, roc_curve
from sklearn.preprocessing import RobustScaler


def _finish(fig: plt.Figure, output: Path) -> list[Path]:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, bbox_inches="tight", facecolor="white")
    svg = output.with_suffix(".svg")
    fig.savefig(svg, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return [output, svg]


def _axes(title: str, xlabel: str, ylabel: str) -> tuple[plt.Figure, plt.Axes]:
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})
    fig, ax = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    ax.set_title(title, pad=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.25, linewidth=0.7)
    return fig, ax


def forecasting_actual_vs_predicted(predictions: pd.DataFrame, output: Path) -> list[Path]:
    daily = predictions.groupby("prediction_date", as_index=False)[["actual", "prediction"]].sum()
    fig, ax = _axes("Forecasting: aggregate actual vs predicted 7-day units", "Prediction date", "Units")
    ax.plot(daily["prediction_date"], daily["actual"], marker="o", label="Actual", color="#1f4e79")
    ax.plot(daily["prediction_date"], daily["prediction"], marker="o", label="Predicted", color="#c55a11")
    ax.legend(frameon=False)
    fig.autofmt_xdate()
    return _finish(fig, output)


def stockout_curves(predictions: pd.DataFrame, pr_output: Path, roc_output: Path) -> list[Path]:
    y = predictions["stockout_within_7d"].astype(int).to_numpy()
    score = predictions["predicted_probability"].to_numpy()
    precision, recall, _ = precision_recall_curve(y, score)
    fpr, tpr, _ = roc_curve(y, score)
    prevalence = float(y.mean())

    fig, ax = _axes("Stockout classification: precision-recall curve", "Recall", "Precision")
    ax.plot(recall, precision, color="#1f4e79", linewidth=1.8, label="Frozen test predictions")
    ax.axhline(prevalence, color="#777777", linestyle="--", label=f"Prevalence ({prevalence:.3f})")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(frameon=False)
    files = _finish(fig, pr_output)

    fig, ax = _axes("Stockout classification: ROC curve", "False-positive rate", "True-positive rate")
    ax.plot(fpr, tpr, color="#1f4e79", linewidth=1.8, label="Frozen test predictions")
    ax.plot([0, 1], [0, 1], color="#777777", linestyle="--", label="Chance")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(frameon=False)
    return files + _finish(fig, roc_output)


def survival_curve(metrics: dict, output: Path) -> list[Path]:
    horizon = metrics["test"]["horizon_metrics"]
    days = sorted(int(day) for day in horizon)
    predicted = [horizon[str(day)]["mean_predicted_survival"] for day in days]
    observed = [horizon[str(day)]["observed_event_free_rate"] for day in days]
    fig, ax = _axes("Stockout survival: test-cohort event-free probability", "Time horizon (days)", "Survival probability")
    ax.plot(days, predicted, marker="o", color="#1f4e79", label="Mean Cox PH prediction")
    ax.plot(days, observed, marker="s", color="#c55a11", label="Observed event-free rate")
    ax.set_xticks(days)
    ax.set_ylim(max(0, min(predicted + observed) - 0.03), 1.002)
    ax.legend(frameon=False)
    return _finish(fig, output)


def segmentation_clusters(dataset: pd.DataFrame, labels: pd.DataFrame, features: list[str], output: Path) -> list[Path]:
    latest = dataset[dataset["snapshot_date"] == dataset["snapshot_date"].max()].copy()
    merged = latest.merge(labels[["store_id", "cluster_id", "segment_name"]], on="store_id", validate="one_to_one")
    matrix = merged[features].astype(float)
    projected = PCA(n_components=2).fit_transform(RobustScaler().fit_transform(matrix))
    fig, ax = _axes("Store segmentation: PCA view of frozen assignments", "PCA component 1", "PCA component 2")
    for cluster_id, group in merged.assign(pc1=projected[:, 0], pc2=projected[:, 1]).groupby("cluster_id"):
        ax.scatter(group["pc1"], group["pc2"], s=46, alpha=0.85, label=f"{cluster_id}: {group['segment_name'].iloc[0]}")
    ax.legend(frameon=False, fontsize=8)
    return _finish(fig, output)


def anomaly_candidates(scores: pd.DataFrame, output: Path) -> list[Path]:
    scoring = scores[scores["period"] == "SCORING"].copy()
    regular = scoring[~scoring["iforest_candidate"]]
    candidates = scoring[scoring["iforest_candidate"]]
    fig, ax = _axes("Anomaly candidates in the scoring period", "Event date", "Observed units")
    ax.scatter(regular["event_date"], regular["event_observed_units"], s=8, alpha=0.12, color="#777777", label="Other observations")
    points = ax.scatter(candidates["event_date"], candidates["event_observed_units"], s=20, alpha=0.7,
                        c=candidates["iforest_anomaly_score"], cmap="Oranges", label="Isolation Forest candidates")
    fig.colorbar(points, ax=ax, label="Anomaly score")
    ax.legend(frameon=False)
    fig.autofmt_xdate()
    return _finish(fig, output)


def basket_rules(rules: pd.DataFrame, output: Path) -> list[Path]:
    labels = rules["antecedent_name"] + " → " + rules["consequent_name"]
    y = np.arange(len(rules))
    fig, ax = _axes("Market basket: selected association rules", "Lift", "Rule")
    scatter = ax.scatter(rules["lift"], y, s=30 + 900 * rules["support"], c=rules["confidence"], cmap="Blues", edgecolor="white")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.axvline(1, color="#777777", linestyle="--", linewidth=1)
    fig.colorbar(scatter, ax=ax, label="Confidence")
    return _finish(fig, output)


def promotion_periods(exposures: pd.DataFrame, output: Path) -> list[Path]:
    eligible = exposures[exposures["eligible_full_cycle"]].copy()
    values = []
    for period in ("pre", "during", "post"):
        units = eligible[f"{period}_realized_units"].sum()
        days = eligible[f"{period}_observed_days"].sum()
        values.append(float(units / days))
    fig, ax = _axes("Promotion performance: observed PRE/DURING/POST comparison\nDescriptive; full-cycle eligible exposures only", "Period", "Aggregate realized units per observed exposure-day")
    bars = ax.bar(["PRE", "DURING", "POST"], values, color=["#7f8c8d", "#1f4e79", "#a5a5a5"])
    ax.bar_label(bars, fmt="%.2f", padding=3)
    return _finish(fig, output)
