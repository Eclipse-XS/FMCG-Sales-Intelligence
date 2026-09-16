from pathlib import Path
import sys

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/refinement"))
from episodes import stockout_episodes


def test_stockout_episode_transition_and_recovery_definition():
    frame = pl.DataFrame({
        "snapshot_date": [
            "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-06"
        ],
        "warehouse_id": [1] * 6,
        "sku_id": [1] * 6,
        "available_quantity": [3, 0, 0, 2, 0, 0],
    }).with_columns(pl.col("snapshot_date").str.to_date())
    result = stockout_episodes(frame)
    assert result.height == 2
    assert result["duration_days"].to_list() == [2, 2]
    assert result["right_censored"].to_list() == [False, True]


def test_refined_generated_inventory_has_multiple_independent_episodes():
    inventory = pl.read_parquet(ROOT / "data/warehouse/raw/inventory.parquet")
    episodes = stockout_episodes(inventory)
    assert episodes.height >= 30
    assert episodes.select(["warehouse_id", "sku_id"]).unique().height >= 20
    assert episodes["episode_start"].n_unique() >= 10
