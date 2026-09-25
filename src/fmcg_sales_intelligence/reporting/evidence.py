"""Build report evidence strictly from materialized frozen artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from .plots import (
    anomaly_candidates,
    basket_rules,
    forecasting_actual_vs_predicted,
    promotion_periods,
    segmentation_clusters,
    stockout_curves,
    survival_curve,
)

CORE_CONFIG = {
    "forecasting": ("forecasting_v1", "forecasting", "Forecasting", "Supervised regression"),
    "stockout": ("stockout_classification_v1", "stockout", "Stockout Classification", "Binary classification"),
    "survival": ("stockout_survival_v1", "survival", "Stockout Survival", "Time-to-event analysis"),
    "segmentation": ("segmentation_v1", "segmentation", "Segmentation", "Unsupervised clustering"),
    "anomaly": ("anomaly_v1", "anomaly", "Anomaly Detection", "Unsupervised candidate detection"),
    "basket": ("basket_v1", "basket", "Market Basket Analysis", "Association-rule mining"),
    "promotion": ("promotion_v1", "promotion", "Promotion Performance", "Descriptive comparison"),
}


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def _write_md_table(path: Path, rows: list[dict[str, Any]], title: str) -> None:
    frame = pd.DataFrame(rows).fillna("")
    headers = [str(column) for column in frame.columns]
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for values in frame.astype(str).itertuples(index=False, name=None):
        lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _metric_rows(metrics: dict[str, Any], prefix: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, value in metrics.items():
        name = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            rows.extend(_metric_rows(value, name))
        elif not isinstance(value, (list, tuple)):
            rows.append({"metric": name, "value": value})
    return rows


def _manifest_entry(root: Path, generated: Path, evidence_type: str, core: str, sources: list[Path], datasets: list[Path], note: str, limitations: list[str]) -> dict[str, Any]:
    return {
        "evidence_type": evidence_type,
        "source_artifacts": [_relative(path, root) for path in sources],
        "source_datasets": [_relative(path, root) for path in datasets],
        "generated_file": _relative(generated, root),
        "core": core,
        "methodology_note": note,
        "limitations_caveats": limitations,
    }


def _add_generated(entries: list[dict[str, Any]], root: Path, files: list[Path], evidence_type: str, core: str,
                   sources: list[Path], datasets: list[Path], note: str, limitations: list[str]) -> None:
    for file in files:
        entries.append(_manifest_entry(root, file, evidence_type, core, sources, datasets, note, limitations))


def _primary(metrics: dict[str, Any], key: str) -> tuple[str, Any, str]:
    if key == "forecasting":
        test = metrics["test"][metrics["selected_model"]]
        return "Test WAPE", test["wape"], f"MAE={test['mae']:.6g}; RMSE={test['rmse']:.6g}"
    if key == "stockout":
        test = metrics["test"]["selected_model"]
        return "Test average precision", test["average_precision"], f"ROC AUC={test['roc_auc']:.6g}; Brier={test['brier']:.6g}"
    if key == "survival":
        test = metrics["test"]
        return "Test concordance index", test["concordance_index"], f"Mean supported-horizon Brier={test['mean_supported_horizon_brier']:.6g}"
    if key == "segmentation":
        return "Silhouette", metrics["selected_silhouette"], f"Davies-Bouldin={metrics['selected_davies_bouldin']:.6g}; retention={metrics['temporal_assignment_retention']:.2%}"
    if key == "anomaly":
        return "Isolation Forest candidate rate", metrics["isolation_forest_candidate_rate"], f"Candidates={metrics['isolation_forest_candidate_count']}; method Jaccard={metrics['jaccard_agreement']:.6g}"
    if key == "basket":
        return "Canonical rule count", metrics["canonical_rule_count"], f"Stable rules={metrics['temporally_stable_rule_count']}; FP-Growth/Apriori consistent={metrics['apriori_fpgrowth_consistent']}"
    return "Aggregate descriptive units change", metrics["aggregate_descriptive_units_change_fraction"], f"Eligible exposures={metrics['pre_vs_during_eligible_exposures']}; baseline sign stability={metrics['baseline_sign_stability']:.2%}"


def _method(artifact: Path) -> str:
    selected = artifact / "selected_model.json"
    obj = _json(selected if selected.exists() else artifact / "selected_method.json")
    for field in ("selected_configuration", "selected_model", "algorithm", "method", "canonical_algorithm", "task_type"):
        if field in obj:
            return str(obj[field])
    return "See canonical method metadata"


def _dataset_path(root: Path, manifest: dict[str, Any]) -> list[Path]:
    fields = ("data_path", "dataset_path", "daily_dataset_path", "exposure_dataset_path")
    return [root / str(manifest[field]).replace("\\", "/") for field in fields if manifest.get(field)]


def _dataset_summary(root: Path) -> list[dict[str, Any]]:
    task_by_dataset = {"forecasting": "Forecasting", "stockout": "Stockout Classification; Stockout Survival", "segmentation": "Segmentation", "anomaly": "Anomaly Detection", "basket": "Market Basket Analysis", "promotion_daily": "Promotion Performance", "promotion_performance": "Promotion Performance"}
    rows = []
    for metadata_path in sorted((root / "data/processed").rglob("*.metadata.json")):
        metadata = _json(metadata_path)
        name = metadata["dataset_name"]
        if name == "segment_assignment":
            continue
        parquet = metadata_path.with_name(metadata_path.name.replace(".metadata.json", ".parquet"))
        dvc = parquet.with_suffix(parquet.suffix + ".dvc")
        rows.append({
            "Dataset": f"{name}_{metadata['dataset_version']}",
            "Task": task_by_dataset.get(name, name),
            "Path": _relative(parquet, root),
            "Grain": ", ".join(metadata["keys"]),
            "Rows": metadata["row_count"],
            "Columns": metadata["column_count"],
            "Primary keys / grain keys": ", ".join(metadata["keys"]),
            "Target / outcome semantics": ", ".join(metadata.get("targets", [])) or "No supervised target",
            "Version / DVC relation": f"{metadata['dataset_version']}; {_relative(dvc, root) if dvc.exists() else 'not DVC-owned'}",
        })
    return rows


def _run_tests(root: Path) -> tuple[dict[str, int], str, str]:
    python = root / ".venv/Scripts/python.exe"
    executable = str(python) if python.exists() else "python"
    collected = subprocess.run([executable, "-m", "pytest", "--collect-only", "-q"], cwd=root, capture_output=True, text=True, check=False)
    categories = {name: len(re.findall(rf"^tests/{name.lower()}/.*::", collected.stdout, flags=re.MULTILINE)) for name in ("Integration", "Runtime", "Scientific", "Unit")}
    run = subprocess.run([executable, "-m", "pytest", "-q"], cwd=root, capture_output=True, text=True, check=False)
    combined = run.stdout + "\n" + run.stderr
    summary_matches = re.findall(
        r"(?m)^([^\r\n]*(?:\d+ passed|\d+ failed|\d+ errors?)[^\r\n]*)$", combined
    )
    summary = summary_matches[-1].strip() if summary_matches else f"pytest exit code {run.returncode}"
    if run.returncode != 0:
        raise RuntimeError(f"pytest failed while generating testing evidence:\n{combined[-4000:]}")
    return categories, summary, datetime.now(timezone.utc).isoformat()


def generate_evidence(root: Path, *, run_tests: bool = True) -> Path:
    root = root.resolve()
    output = root / "report/evidence"
    output.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    entries: list[dict[str, Any]] = []
    unsupported: list[dict[str, str]] = []
    summaries: list[dict[str, Any]] = []
    registry = _json(root / "artifacts/project/modeling_registry_v1.json")
    registry_status = {item["task"]: item["status"] for item in registry["cores"]}

    for key, (artifact_name, directory, display, task) in CORE_CONFIG.items():
        artifact = root / "artifacts/canonical" / artifact_name
        metrics_path = artifact / "metrics.json"
        manifest_path = artifact / "manifest.json"
        metrics, manifest = _json(metrics_path), _json(manifest_path)
        datasets = _dataset_path(root, manifest)
        primary_name, primary_value, secondary = _primary(metrics, key)
        summaries.append({"Core": display, "Task": task, "Method": _method(artifact), "Primary Metric": primary_name,
                          "Primary Metric Value": primary_value, "Secondary Metrics": secondary,
                          "Dataset": "; ".join(_relative(path, root) for path in datasets), "Artifact Version": artifact_name,
                          "Status": registry_status.get("stockout_classification" if key == "stockout" else "stockout_survival" if key == "survival" else key, manifest.get("readiness", manifest.get("status", "complete")))})
        metrics_output = output / directory / "metrics.csv"
        _write_csv(metrics_output, _metric_rows(metrics))
        entries.append(_manifest_entry(root, metrics_output, "metrics_table", display, [metrics_path, manifest_path], datasets,
                                       "Canonical metrics flattened without recomputation.", []))

        if key == "forecasting":
            source = artifact / "predictions/test_predictions.parquet"
            files = forecasting_actual_vs_predicted(pd.read_parquet(source), output / directory / "actual_vs_predicted.png")
            _add_generated(entries, root, files, "figure", display, [source], datasets, "Daily aggregate of frozen out-of-sample actual and predicted 7-day units.", ["Aggregation hides store-SKU variation."])
        elif key == "stockout":
            source = artifact / "predictions/test_predictions.parquet"
            frame = pd.read_parquet(source)
            files = stockout_curves(frame, output / directory / "precision_recall.png", output / directory / "roc_curve.png")
            derived = {"average_precision": average_precision_score(frame["stockout_within_7d"], frame["predicted_probability"]), "roc_auc": roc_auc_score(frame["stockout_within_7d"], frame["predicted_probability"])}
            for metric, value in derived.items():
                if abs(value - float(metrics["test"]["selected_model"][metric])) > 1e-12:
                    raise ValueError(f"Frozen stockout {metric} does not match canonical metrics")
            _add_generated(entries, root, files, "figure", display, [source, metrics_path], datasets, "Curves computed from frozen out-of-sample labels and probabilities; no model inference or fitting.", ["Rare-event prevalence affects precision."])
        elif key == "survival":
            files = survival_curve(metrics, output / directory / "survival_curve.png")
            _add_generated(entries, root, files, "figure", display, [metrics_path], datasets, "Mean predicted survival and observed event-free rate at supported test horizons.", ["Not a classification probability; the risk set is censored and limited to seven days."])
        elif key == "segmentation":
            label_source = artifact / "predictions_or_labels/store_segments.parquet"
            dataset_source = datasets[0]
            labels, dataset = pd.read_parquet(label_source), pd.read_parquet(dataset_source)
            sizes = labels.groupby(["cluster_id", "segment_name"], as_index=False).size().rename(columns={"size": "store_count"})
            size_output = output / directory / "cluster_sizes.csv"
            sizes.to_csv(size_output, index=False)
            entries.append(_manifest_entry(root, size_output, "cluster_sizes", display, [label_source], datasets, "Counts of frozen reference-snapshot cluster assignments.", ["Cluster identifiers are exploratory pseudo-labels."]))
            features = _json(artifact / "selected_model.json")["features"]
            files = segmentation_clusters(dataset, labels, features, output / directory / "clusters.png")
            _add_generated(entries, root, files, "figure", display, [label_source, artifact / "selected_model.json"], datasets, "PCA is used only for two-dimensional visualization of frozen cluster assignments.", ["PCA geometry is illustrative and does not refit or alter KMeans."])
        elif key == "anomaly":
            score_source = artifact / "predictions_or_scores/anomaly_scores.parquet"
            scores = pd.read_parquet(score_source)
            candidates = scores[scores["iforest_candidate"]].sort_values("iforest_anomaly_score", ascending=False).head(20)
            columns = ["event_date", "store_id", "sku_id", "event_observed_units", "event_is_promo", "iforest_anomaly_score", "zscore_candidate", "method_agreement", "review_status"]
            example_output = output / directory / "anomaly_examples.csv"
            candidates[columns].to_csv(example_output, index=False)
            entries.append(_manifest_entry(root, example_output, "candidate_examples", display, [score_source], datasets, "Top 20 frozen Isolation Forest candidates ranked by anomaly score.", ["Candidates are not confirmed errors, fraud, or events; no ground truth exists."]))
            files = anomaly_candidates(scores, output / directory / "anomaly_candidates.png")
            _add_generated(entries, root, files, "figure", display, [score_source], datasets, "Frozen scoring-period observations with Isolation Forest candidates highlighted.", ["Candidate density and units do not establish root cause."])
        elif key == "basket":
            rules_source = artifact / "outputs/top_rules.csv"
            stability_source = artifact / "diagnostics/temporal_stability.csv"
            rules, stability = pd.read_csv(rules_source), pd.read_csv(stability_source)
            stable_ids = set(stability.loc[stability["stability_status"] == "STABLE", "rule_id"])
            eligible = rules[rules["rule_id"].isin(stable_ids)].copy()
            if eligible.empty:
                eligible = rules.copy()
            eligible["ranking_score"] = eligible["support"] * eligible["confidence"] * eligible["lift"]
            top = eligible.sort_values(["ranking_score", "support"], ascending=False).head(15)
            columns = ["antecedent_name", "consequent_name", "support", "confidence", "lift", "support_count", "rule_id", "ranking_score"]
            rules_output = output / directory / "top_rules.csv"
            top[columns].to_csv(rules_output, index=False)
            entries.append(_manifest_entry(root, rules_output, "top_rules", display, [rules_source, stability_source], datasets, "Top 15 temporally stable canonical rules by support × confidence × lift; canonical support threshold already applies.", ["Associations are descriptive and are not recommendations or causal relations."]))
            files = basket_rules(top, output / directory / "top_rules.png")
            _add_generated(entries, root, files, "figure", display, [rules_source, stability_source], datasets, "Lift by rule; marker size encodes support and color encodes confidence.", ["Only selected stable rules are shown."])
        elif key == "promotion":
            source = artifact / "outputs/exposure_metrics.parquet"
            exposures = pd.read_parquet(source)
            summary_source = artifact / "outputs/promotion_summary.parquet"
            promotion_summary = pd.read_parquet(summary_source)
            summary_output = output / directory / "promotion_summary.csv"
            promotion_summary.to_csv(summary_output, index=False)
            entries.append(_manifest_entry(root, summary_output, "promotion_summary", display, [summary_source], datasets, "Canonical promotion-level descriptive summary exported to CSV.", ["Observed changes are non-causal; only three physical promotions are available."]))
            if exposures["eligible_full_cycle"].any():
                files = promotion_periods(exposures, output / directory / "pre_during_post.png")
                _add_generated(entries, root, files, "figure", display, [source], datasets, "PRE/DURING/POST realized units per observed exposure-day among full-cycle eligible exposures.", ["Descriptive comparison only; full-cycle evidence is limited to one promotion cohort."])
            else:
                unsupported.append({"core": display, "output": "promotion/pre_during_post.png", "reason": "No full-cycle eligible frozen exposures."})

    summary_dir = output / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = summary_dir / "scientific_cores_summary.csv"
    summary_md = summary_dir / "scientific_cores_summary.md"
    _write_csv(summary_csv, summaries)
    _write_md_table(summary_md, summaries, "Scientific Cores Summary")
    datasets = _dataset_summary(root)
    datasets_csv = summary_dir / "datasets_summary.csv"
    datasets_md = summary_dir / "datasets_summary.md"
    _write_csv(datasets_csv, datasets)
    _write_md_table(datasets_md, datasets, "Published Dataset Summary")

    testing_md = summary_dir / "testing_summary.md"
    if run_tests:
        categories, pytest_summary, tested_at = _run_tests(root)
        testing = ["# Testing Summary", "", f"Validation timestamp (UTC): `{tested_at}`", "", f"Full-suite result: **{pytest_summary}**", "", "| Category | Collected tests |", "| --- | ---: |"]
        testing.extend(f"| {name} | {count} |" for name, count in categories.items())
        testing.extend(["", f"Total collected: **{sum(categories.values())}**", "", "Counts are derived from `pytest --collect-only -q`; the result is from a separate full `pytest -q` run."])
    else:
        testing = ["# Testing Summary", "", "Not regenerated: generator invoked with `--skip-tests`."]
    testing_md.write_text("\n".join(testing) + "\n", encoding="utf-8")

    common_sources = [root / "artifacts/project/modeling_registry_v1.json"]
    for file, kind in ((summary_csv, "cross_core_summary"), (summary_md, "cross_core_summary"), (datasets_csv, "dataset_summary"), (datasets_md, "dataset_summary"), (testing_md, "testing_summary")):
        entries.append(_manifest_entry(root, file, kind, "Cross-project", common_sources, [], "Generated from canonical metadata, processed dataset contracts, and/or the current pytest run.", []))

    readme = output / "README.md"
    readme.write_text(
        "# Reproducible Report Evidence\n\n"
        "Generated exclusively from materialized canonical artifacts and processed-dataset metadata. The generator does not train models, write canonical artifacts, or modify DVC state.\n\n"
        "## Reproduce\n\n```powershell\n.\\.venv\\Scripts\\python.exe scripts\\generate_report_evidence.py\n```\n\n"
        "Use `--skip-tests` only for a faster local refresh; that mode explicitly marks testing evidence as not regenerated.\n\n"
        "## Methodological boundaries\n\n"
        "- Classification curves are derived from frozen out-of-sample labels and probabilities, without model inference.\n"
        "- PCA is used only for two-dimensional visualization of frozen cluster assignments.\n"
        "- Anomalies are review candidates, not confirmed errors, fraud, or events.\n"
        "- Basket rules are associations, not causal relations or recommendations.\n"
        "- Promotion results are descriptive observed comparisons, not causal effects, incrementality, or ROI.\n"
        "- Every PNG figure has a matching SVG. Traceability and limitations are recorded in `summary/evidence_manifest.json`.\n\n"
        "## Unsupported evidence\n\n" + ("\n".join(f"- {item['output']}: {item['reason']}" for item in unsupported) if unsupported else "No requested evidence was omitted.") + "\n",
        encoding="utf-8",
    )
    entries.append(_manifest_entry(root, readme, "package_documentation", "Cross-project", common_sources, [], "Documents reproduction and interpretation boundaries.", []))

    for entry in entries:
        path = root / entry["generated_file"]
        entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        entry["generated_at"] = generated_at
    evidence_manifest = {"schema_version": "1.0", "generated_at": generated_at, "generator": "scripts/generate_report_evidence.py", "outputs": entries, "unsupported_evidence": unsupported}
    manifest_output = summary_dir / "evidence_manifest.json"
    manifest_output.write_text(json.dumps(evidence_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output
