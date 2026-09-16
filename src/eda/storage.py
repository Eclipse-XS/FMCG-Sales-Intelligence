from __future__ import annotations
import json,shutil
from pathlib import Path
from .errors import CorruptRunError,RunNotFoundError
from .models import ArtifactReference,DatasetIdentity,EDAResult,Finding,Readiness,Severity
from .reporting import create_figures,render_markdown

class RunStore:
    def __init__(self,root:Path): self.root=root;self.runs=root/"runs"
    def _portable(self,path:Path)->str:
        try:return str(path.resolve().relative_to(self.root.parents[1].resolve())).replace("\\","/")
        except ValueError:return str(path)
    def persist(self,result:EDAResult)->EDAResult:
        directory=self.runs/result.run_id;directory.mkdir(parents=True,exist_ok=False)
        try:
            result.artifacts.extend(create_figures(result,directory/"figures"))
            for ref in result.artifacts:ref.path=self._portable(Path(ref.path))
            report=directory/"report.md";report.write_text(render_markdown(result),encoding="utf-8");result.artifacts.append(ArtifactReference("report",self._portable(report)))
            metrics=directory/"metrics.json";metrics.write_text(json.dumps(result.to_dict()["metrics"],indent=2,allow_nan=False),encoding="utf-8");result.artifacts.append(ArtifactReference("metrics",self._portable(metrics)))
            findings=directory/"findings.json";findings.write_text(json.dumps(result.to_dict()["findings"],indent=2,allow_nan=False),encoding="utf-8");result.artifacts.append(ArtifactReference("findings",self._portable(findings)))
            manifest=directory/"manifest.json";result.artifacts.append(ArtifactReference("manifest",self._portable(manifest)));manifest.write_text(json.dumps(result.to_dict(),indent=2,allow_nan=False),encoding="utf-8")
            latest=self.root/"latest.json";latest.parent.mkdir(parents=True,exist_ok=True);latest.write_text(json.dumps({"run_id":result.run_id,"task":result.analysis_type,"manifest":self._portable(manifest)},indent=2),encoding="utf-8")
            return result
        except Exception:
            shutil.rmtree(directory)
            raise
    def list(self,task:str|None=None)->list[dict]:
        if not self.runs.exists():return []
        items=[]
        for p in self.runs.glob("*/manifest.json"):
            try:
                x=json.loads(p.read_text(encoding="utf-8"))
                if task is None or x["analysis_type"]==task:items.append({"run_id":x["run_id"],"task":x["analysis_type"],"generated_at":x["generated_at"],"status":x["status"]})
            except (KeyError,json.JSONDecodeError):continue
        return sorted(items,key=lambda x:x["generated_at"],reverse=True)
    def load(self,run_id:str)->EDAResult:
        p=self.runs/run_id/"manifest.json"
        if not p.exists():raise RunNotFoundError(f"Unknown EDA run: {run_id}")
        try:x=json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:raise CorruptRunError(f"Corrupt manifest: {p}") from exc
        try:return EDAResult(x["run_id"],x["analysis_type"],x["generated_at"],x["status"],[DatasetIdentity(**d) for d in x["datasets"]],x["metrics"],x["profile"],[Finding(code=f["code"],severity=Severity(f["severity"]),message=f["message"],metric=f.get("metric"),recommendation=f.get("recommendation"),evidence=f.get("evidence",{})) for f in x["findings"]],{k:Readiness(v) for k,v in x["readiness"].items()},[ArtifactReference(**a) for a in x.get("artifacts",[])],x.get("elapsed_seconds",0),x.get("error"))
        except (KeyError,TypeError,ValueError) as exc:raise CorruptRunError(f"Invalid manifest schema: {p}") from exc
    def latest(self,task:str)->EDAResult:
        runs=self.list(task)
        if not runs:raise RunNotFoundError(f"No runs for task: {task}")
        return self.load(runs[0]["run_id"])
