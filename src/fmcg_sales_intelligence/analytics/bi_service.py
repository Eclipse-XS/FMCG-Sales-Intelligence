from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from ..common.paths import project_path


class BusinessIntelligenceService:
    """Read-only fixed analytical queries; no arbitrary SQL is exposed."""

    def __init__(self, database: str | Path | None = None):
        self.database = Path(database) if database else project_path("data", "warehouse", "fmcg.duckdb")

    def _connect(self):
        if not self.database.exists():
            raise FileNotFoundError("Local analytical warehouse is unavailable")
        return duckdb.connect(str(self.database), read_only=True)

    def summary(self) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("""select min(sale_date), max(sale_date), coalesce(sum(units_sold),0),
                coalesce(sum(net_revenue),0), coalesce(sum(net_revenue)/nullif(sum(units_sold),0),0),
                count(distinct store_id), count(distinct sku_id) from analytics.mart_sales_daily""").fetchone()
        return {
            "date_from": str(row[0]),
            "date_to": str(row[1]),
            "units": int(row[2]),
            "revenue": float(row[3]),
            "average_selling_price": float(row[4]),
            "active_stores": int(row[5]),
            "active_skus": int(row[6]),
            "freshness_note": "Historical synthetic local warehouse; not live data.",
        }

    def timeseries(self, limit: int = 120) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """select sale_date, sum(units_sold) units, sum(net_revenue) revenue
                from analytics.mart_sales_daily group by sale_date order by sale_date desc limit ?""",
                [limit],
            ).fetchall()
        return [{"date": str(d), "units": int(u), "revenue": float(r)} for d, u, r in reversed(rows)]

    def breakdown(self, dimension: str, limit: int = 20) -> list[dict[str, Any]]:
        allowed = {
            "brand": "brand_name",
            "category": "category_name",
            "region": "region_id",
            "channel": "channel",
            "store": "store_id",
        }
        if dimension not in allowed:
            raise ValueError("Unsupported breakdown dimension")
        column = allowed[dimension]
        query = f"""select {column}, sum(units_sold) units, sum(net_revenue) revenue
            from analytics.mart_sales_daily group by {column} order by revenue desc limit ?"""
        with self._connect() as conn:
            rows = conn.execute(query, [limit]).fetchall()
        return [
            {"key": str(key), "units": int(units), "revenue": float(revenue)} for key, units, revenue in rows
        ]
