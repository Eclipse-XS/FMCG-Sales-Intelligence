from __future__ import annotations

import logging
from typing import Any
import duckdb
from pathlib import Path
import numpy as np

from ...common.paths import project_path

LOGGER = logging.getLogger("fsi.resolver")

class FeatureResolver:
    def __init__(self, data_root: Path | None = None):
        self.data_root = data_root or project_path("data", "processed")

    def _query_latest(self, dataset: str, filters: dict[str, Any], order_by: str) -> dict[str, Any] | None:
        parquet_path = self.data_root / dataset / f"{dataset}_v1.parquet"
        if not parquet_path.exists():
            raise RuntimeError(f"Processed dataset {dataset} not found at {parquet_path}")

        conditions = []
        params = []
        for k, v in filters.items():
            conditions.append(f"{k} = ?")
            params.append(v)
            
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"SELECT * FROM '{parquet_path}' WHERE {where_clause} ORDER BY {order_by} DESC LIMIT 1"
        
        try:
            with duckdb.connect(":memory:") as conn:
                df = conn.execute(sql, params).fetchdf()
                if df.empty:
                    return None
                # Clean up NaN / Inf for JSON serialization
                df = df.replace([np.inf, -np.inf], np.nan).fillna(np.nan)
                record = df.to_dict(orient="records")[0]
                # Replace nan with None
                for k, v in record.items():
                    if isinstance(v, float) and np.isnan(v):
                        record[k] = None
                        
                # Strip forbidden outcome variables to prevent leakage validation errors
                forbidden = {
                    "observed_units", "target_units_next_7d", "target_requested_demand_next_7d", "target_lost_sales_next_7d", "realized_transaction_unit_price",
                    "first_stockout_date", "stockout_within_7d", "event_observed", "event_time_days", "censor_time_days", "horizon_complete", "target_observed_next_7d"
                }
                for k in list(record.keys()):
                    if k in forbidden:
                        del record[k]
                        
                return record
        except Exception as e:
            LOGGER.error("Feature resolution failed", exc_info=True)
            raise RuntimeError(f"Failed to resolve features for {dataset}: {e}")

    def resolve_forecast_features(self, store_id: int, sku_id: int) -> dict[str, Any] | None:
        return self._query_latest(
            dataset="forecasting",
            filters={"store_id": store_id, "sku_id": sku_id},
            order_by="prediction_date"
        )

    def resolve_stockout_features(self, warehouse_id: int, sku_id: int) -> dict[str, Any] | None:
        return self._query_latest(
            dataset="stockout",
            filters={"warehouse_id": warehouse_id, "sku_id": sku_id},
            order_by="prediction_date"
        )

    def resolve_segmentation_features(self, store_id: int) -> dict[str, Any] | None:
        record = self._query_latest(
            dataset="segment_assignment",
            filters={"store_id": store_id},
            order_by="snapshot_date"
        )
        if record:
            allowed = {"store_id", "revenue_30d", "average_price_30d", "promotion_unit_share_30d", "revenue_volatility_30d"}
            for k in list(record.keys()):
                if k not in allowed:
                    del record[k]
        return record
