from __future__ import annotations
import argparse
import json
import sys
from .comparison import compare_runs
from .config import EDAConfig
from .errors import EDAError
from .service import run_eda
from .storage import RunStore

def parser():
    p=argparse.ArgumentParser(prog="python -m fmcg_sales_intelligence.science.eda.cli");sub=p.add_subparsers(dest="command",required=True)
    run=sub.add_parser("run");run.add_argument("--task",default="all");run.add_argument("--dataset")
    lr=sub.add_parser("list-runs");lr.add_argument("--task")
    show=sub.add_parser("show-run");show.add_argument("run_id")
    latest=sub.add_parser("latest");latest.add_argument("--task",required=True)
    comp=sub.add_parser("compare");comp.add_argument("run_a");comp.add_argument("run_b")
    return p
def main(argv=None)->int:
    args=parser().parse_args(argv);store=RunStore(EDAConfig().report_root)
    try:
        if args.command=="run":out=run_eda(args.task,args.dataset).to_dict()
        elif args.command=="list-runs":out=store.list(args.task)
        elif args.command=="show-run":out=store.load(args.run_id).to_dict()
        elif args.command=="latest":out=store.latest(args.task).to_dict()
        else:out=compare_runs(store.load(args.run_a),store.load(args.run_b)).to_dict()
        print(json.dumps(out,indent=2,default=str,allow_nan=False));return 0
    except EDAError as exc:
        print(f"EDA error: {exc}",file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
