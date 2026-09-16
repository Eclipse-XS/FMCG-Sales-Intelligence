"""Physical stockout episode extraction from daily inventory snapshots."""
from __future__ import annotations

from datetime import date
import polars as pl


def stockout_episodes(inventory: pl.DataFrame) -> pl.DataFrame:
    """Return >0 -> <=0 episodes, closed by the first later >0 snapshot."""
    records: list[dict] = []
    ordered = inventory.sort(["warehouse_id", "sku_id", "snapshot_date"])
    for (warehouse_id, sku_id), series in ordered.group_by(
        ["warehouse_id", "sku_id"], maintain_order=True
    ):
        active: date | None = None
        previous_positive = True
        for row in series.iter_rows(named=True):
            current_positive = row["available_quantity"] > 0
            if active is None and previous_positive and not current_positive:
                active = row["snapshot_date"]
            elif active is not None and current_positive:
                end = row["snapshot_date"]
                records.append({
                    "warehouse_id": warehouse_id,
                    "sku_id": sku_id,
                    "episode_start": active,
                    "recovery_date": end,
                    "duration_days": (end - active).days,
                    "right_censored": False,
                })
                active = None
            previous_positive = current_positive
        if active is not None:
            end = series["snapshot_date"].max()
            records.append({
                "warehouse_id": warehouse_id,
                "sku_id": sku_id,
                "episode_start": active,
                "recovery_date": None,
                "duration_days": (end - active).days + 1,
                "right_censored": True,
            })
    schema = {
        "warehouse_id": pl.Int64,
        "sku_id": pl.Int64,
        "episode_start": pl.Date,
        "recovery_date": pl.Date,
        "duration_days": pl.Int64,
        "right_censored": pl.Boolean,
    }
    return pl.DataFrame(records, schema=schema) if records else pl.DataFrame(schema=schema)
