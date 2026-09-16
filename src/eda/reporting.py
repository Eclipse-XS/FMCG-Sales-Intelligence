from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .models import ArtifactReference, EDAResult

def render_markdown(result: EDAResult) -> str:
    lines=[f"# EDA run: {result.analysis_type}","",f"- Run ID: `{result.run_id}`",f"- Generated: `{result.generated_at}`",f"- Status: **{result.status}**",f"- Elapsed: {result.elapsed_seconds:.3f}s","","## Inputs",""]
    for d in result.datasets: lines.append(f"- `{d.logical_name}`: {d.row_count:,} rows, SHA-256 `{d.content_sha256}`, schema `{d.schema_sha256}`")
    lines += ["","## Readiness",""]+[f"- {k}: **{v.value}**" for k,v in result.readiness.items()]
    lines += ["","## Findings",""]
    for x in result.findings:
        lines.append(f"- `{x.severity.value}` `{x.code}` — {x.message}" + (f" Metric: {x.metric}." if x.metric is not None else "") + (f" Recommendation: {x.recommendation}" if x.recommendation else ""))
    lines += ["","## Metrics","","```json",json.dumps(result.to_dict()["metrics"],indent=2,allow_nan=False),"```",""]
    return "\n".join(lines)

def create_figures(result: EDAResult, directory: Path) -> list[ArtifactReference]:
    directory.mkdir(parents=True,exist_ok=True); refs=[]
    if result.analysis_type in ("forecasting","all"):
        m=result.metrics.get("forecasting",result.metrics)
        if "complete_target_rows" in m:
            fig,ax=plt.subplots(figsize=(6,4));ax.bar(["complete","incomplete"],[m["complete_target_rows"],m["target_incomplete_rows"]],color=["#2563eb","#94a3b8"]);ax.set_title("Seven-day target coverage");fig.tight_layout();p=directory/"forecast_target_coverage.png";fig.savefig(p,dpi=180);plt.close(fig);refs.append(ArtifactReference("figure",str(p)))
    if result.analysis_type in ("stockout","all"):
        m=result.metrics.get("stockout",result.metrics)
        if "positive_horizons" in m:
            fig,ax=plt.subplots(figsize=(6,4));ax.bar(["positive","complete non-event","incomplete"],[m["positive_horizons"],m["complete_non_events"],m["incomplete_non_events"]],color=["#dc2626","#2563eb","#f59e0b"]);ax.set_yscale("log");ax.set_title("Stockout outcomes");fig.tight_layout();p=directory/"stockout_outcomes.png";fig.savefig(p,dpi=180);plt.close(fig);refs.append(ArtifactReference("figure",str(p)))
    return refs
