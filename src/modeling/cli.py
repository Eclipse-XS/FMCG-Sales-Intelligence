from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from . import run_experiment


def main():
    parser = argparse.ArgumentParser(description="Run leakage-safe forecasting experiments")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--task", choices=["forecasting", "stockout_classification", "stockout_survival", "segmentation", "anomaly", "basket", "promotion"], required=True)
    run.add_argument("--config")
    run.add_argument("--data")
    run.add_argument("--output")
    run.add_argument("--experiment-id")
    run.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    defaults = {
        "forecasting": ("configs/modeling/forecasting.yaml", "data/processed/forecasting/forecasting_v1.parquet"),
        "stockout_classification": ("configs/modeling/stockout_classification.yaml", "data/processed/stockout/stockout_v1.parquet"),
        "stockout_survival": ("configs/modeling/stockout_survival.yaml", "data/processed/stockout/stockout_v1.parquet"),
        "segmentation": ("configs/modeling/segmentation.yaml", "data/processed/segmentation/segmentation_v1.parquet"),
        "anomaly": ("configs/modeling/anomaly.yaml", "data/processed/anomaly/anomaly_v1.parquet"),
        "basket": ("configs/modeling/basket.yaml", "data/processed/basket/basket_v1.parquet"),
        "promotion": ("configs/modeling/promotion.yaml", "data/processed/promotion_daily/promotion_daily_v1.parquet"),
    }
    config, data = defaults[args.task]
    result = run_experiment(args.task, config_path=args.config or config, data_path=args.data or data,
                            output_dir=args.output, experiment_id=args.experiment_id, overwrite=args.overwrite)
    result_dir = Path(result.output_dir if hasattr(result, "output_dir") else result["output_dir"])
    canonical = {"forecasting": "artifacts/canonical/forecasting_v1", "stockout_classification": "artifacts/canonical/stockout_classification_v1", "stockout_survival": "artifacts/canonical/stockout_survival_v1", "segmentation": "artifacts/canonical/segmentation_v1", "anomaly": "artifacts/canonical/anomaly_v1", "basket": "artifacts/canonical/basket_v1", "promotion": "artifacts/canonical/promotion_v1"}
    metric_paths = {"forecasting": "artifacts/forecasting_v1_metrics.json", "stockout_classification": "artifacts/stockout_classification_v1_metrics.json", "stockout_survival": "artifacts/stockout_survival_v1_metrics.json", "segmentation": "artifacts/segmentation_v1_metrics.json", "anomaly": "artifacts/anomaly_v1_metrics.json", "basket": "artifacts/basket_v1_metrics.json", "promotion": "artifacts/promotion_v1_metrics.json"}
    if args.output and Path(args.output).as_posix() == canonical[args.task]:
        shutil.copy2(result_dir / "dvc_metrics.json", metric_paths[args.task])
    if hasattr(result, "experiment_id"):
        payload={"experiment_id":result.experiment_id,"output_dir":str(result.output_dir),"selected_model":result.selected_model,"test_metrics":result.test_metrics}
    else: payload=result
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
