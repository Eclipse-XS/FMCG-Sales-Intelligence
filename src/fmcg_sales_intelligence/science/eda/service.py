from __future__ import annotations
import hashlib
import logging
import time
import uuid
from datetime import datetime,timezone
from pathlib import Path
from .analyzers import analyze
from .config import EDAConfig,SUPPORTED_TASKS
from .errors import UnknownTaskError
from .models import EDARequest,EDAResult,Finding,Readiness,Severity
from .profiling import fingerprint,load_dataset,profile
from .storage import RunStore

log=logging.getLogger(__name__)

class EDAService:
    def __init__(self,config:EDAConfig|None=None):self.config=config or EDAConfig();self.store=RunStore(self.config.report_root)
    def run(self,request:EDARequest)->EDAResult:
        started=time.perf_counter();task=request.task.lower()
        if task not in (*SUPPORTED_TASKS,"all"):raise UnknownTaskError(f"Unknown task '{task}'. Supported: all, {', '.join(SUPPORTED_TASKS)}")
        if request.dataset_path and task in ("all","general"):raise UnknownTaskError("A single dataset override is not valid for all/general")
        tasks=list(self.config.default_paths) if task in ("all","general") else [task]
        frames={};identities=[]
        for name in tasks:
            path=Path(request.dataset_path).expanduser().resolve() if request.dataset_path else self.config.default_paths[name]
            frame=load_dataset(path);frames[name]=(frame,path);identity=fingerprint(path,name,frame)
            try: identity.path=str(path.resolve().relative_to(self.config.project_root.resolve())).replace("\\","/")
            except ValueError: pass
            identities.append(identity)
        seed="".join(x.content_sha256 for x in identities).encode();short=hashlib.sha256(seed).hexdigest()[:10]
        run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")+f"_{short}_{uuid.uuid4().hex[:6]}"
        metrics={};profiles={};findings=[];readiness={}
        if task=="general":
            for name,(frame,_) in frames.items():profiles[name]=profile(frame)
            metrics={"datasets":{n:{"rows":f.height,"columns":f.width} for n,(f,_) in frames.items()}}
            readiness={"general":Readiness.NOT_APPLICABLE};findings=[Finding("GENERAL_PROFILE_COMPLETE",Severity.INFO,"All supported datasets were profiled.",len(frames))]
        else:
            for name,(frame,path) in frames.items():
                m,p,fs,r=analyze(name,frame,path,self.config);metrics[name]=m;profiles[name]=p;findings.extend(fs);readiness.update(r)
            if task!="all":metrics=metrics[task];profiles=profiles[task]
        result=EDAResult(run_id,task,datetime.now(timezone.utc).isoformat(),"COMPLETED",identities,metrics,profiles,findings,readiness,elapsed_seconds=time.perf_counter()-started)
        if request.persist:self.store.persist(result)
        log.info("EDA completed task=%s run_id=%s elapsed=%.3fs",task,run_id,result.elapsed_seconds)
        return result

def run_eda(task:str="all",dataset_path:str|Path|None=None,persist:bool=True,config:EDAConfig|None=None)->EDAResult:
    return EDAService(config).run(EDARequest(task,Path(dataset_path) if dataset_path else None,persist))
