from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .forecasting import run_experiment


def main():
    parser = argparse.ArgumentParser(description="Run leakage-safe forecasting experiments")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--task", choices=["forecasting"], required=True)
    run.add_argument("--config", default="configs/modeling/forecasting.yaml")
    run.add_argument("--data", default="data/processed/forecasting/forecasting_v1.parquet")
    run.add_argument("--output")
    run.add_argument("--experiment-id")
    run.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    result = run_experiment(config_path=args.config, data_path=args.data, output_dir=args.output,
                            experiment_id=args.experiment_id, overwrite=args.overwrite)
    if args.output and Path(args.output).as_posix() == "artifacts/canonical/forecasting_v1":
        shutil.copy2(result.output_dir / "dvc_metrics.json", "artifacts/forecasting_v1_metrics.json")
    print(json.dumps({"experiment_id": result.experiment_id, "output_dir": str(result.output_dir),
                      "selected_model": result.selected_model, "test_metrics": result.test_metrics}, indent=2))


if __name__ == "__main__":
    main()
