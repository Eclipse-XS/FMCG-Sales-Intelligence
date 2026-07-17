from __future__ import annotations

from fmcg_sales_intelligence.common.paths import PROJECT_ROOT
from dataclasses import dataclass, field
from pathlib import Path

ROOT = PROJECT_ROOT

@dataclass(frozen=True)
class EDAConfig:
    project_root: Path = ROOT
    report_root: Path = ROOT / "artifacts" / "reports" / "eda"
    processed_root: Path = ROOT / "data" / "processed"
    warehouse_root: Path = ROOT / "data" / "warehouse"
    random_seed: int = 42
    top_n: int = 15
    target_coverage_warning: float = 0.80
    target_coverage_critical: float = 0.50
    stockout_episode_warning: int = 30
    null_rate_change_warning: float = 0.10

    default_paths: dict[str, Path] = field(default_factory=lambda: {
        "forecasting": ROOT / "data/processed/forecasting/forecasting_v1.parquet",
        "stockout": ROOT / "data/processed/stockout/stockout_v1.parquet",
        "segmentation": ROOT / "data/processed/segmentation/segmentation_v1.parquet",
        "anomaly": ROOT / "data/processed/anomaly/anomaly_v1.parquet",
        "basket": ROOT / "data/processed/basket/basket_v1.parquet",
        "promotion": ROOT / "data/processed/promotion_performance/promotion_performance_v1.parquet",
    })

SUPPORTED_TASKS = ("general", "forecasting", "stockout", "segmentation", "anomaly", "basket", "promotion")
