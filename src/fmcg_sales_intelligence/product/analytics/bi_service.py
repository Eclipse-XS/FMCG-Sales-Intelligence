from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from ...common.paths import project_path
from .filters import AnalyticsFilters


class BusinessIntelligenceService:
    """Read-only fixed analytical queries; no arbitrary SQL is exposed."""

    def __init__(self, database: str | Path | None = None):
        self.database = Path(database) if database else project_path("data", "warehouse", "fmcg.duckdb")

    def _connect(self):
        if not self.database.exists():
            raise FileNotFoundError("Local analytical warehouse is unavailable")
        return duckdb.connect(str(self.database), read_only=True)

    @staticmethod
    def _where(filters: AnalyticsFilters) -> tuple[str, list[Any]]:
        filters.validate_range()
        clauses: list[str] = []
        parameters: list[Any] = []
        scalar = (("date_from", "sale_date >= ?"), ("date_to", "sale_date <= ?"))
        for field, expression in scalar:
            value = getattr(filters, field)
            if value is not None:
                clauses.append(expression)
                parameters.append(value)
        sequences = (
            ("regions", "region_id"), ("channels", "channel"), ("stores", "store_id"),
            ("categories", "category_name"), ("brands", "brand_name"), ("skus", "sku_id"),
        )
        for field, column in sequences:
            values = getattr(filters, field)
            if values:
                clauses.append(f"{column} in ({','.join('?' for _ in values)})")
                parameters.extend(values)
        if filters.promotion is not None:
            clauses.append("promo_units > 0" if filters.promotion else "promo_units = 0")
        return (" where " + " and ".join(clauses) if clauses else ""), parameters

    def filter_metadata(self) -> dict[str, Any]:
        with self._connect() as conn:
            start, end = conn.execute(
                "select min(sale_date), max(sale_date) from analytics.mart_sales_daily"
            ).fetchone()
            result: dict[str, Any] = {"date_from": str(start), "date_to": str(end)}
            for public, column in {
                "regions": "region_id", "channels": "channel", "stores": "store_id",
                "categories": "category_name", "brands": "brand_name", "skus": "sku_id",
            }.items():
                rows = conn.execute(
                    f"select distinct {column} from analytics.mart_sales_daily "
                    f"where {column} is not null order by {column} limit 500"
                ).fetchall()
                result[public] = [row[0] for row in rows]
        result["promotions"] = [False, True]
        result["semantics"] = "Inclusive calendar-date filters over historical realized sales."
        return result

    def summary(self, filters: AnalyticsFilters | None = None) -> dict[str, Any]:
        where, parameters = self._where(filters or AnalyticsFilters())
        with self._connect() as conn:
            row = conn.execute(f"""select min(sale_date), max(sale_date), coalesce(sum(units_sold),0),
                coalesce(sum(net_revenue),0), coalesce(sum(net_revenue)/nullif(sum(units_sold),0),0),
                count(distinct store_id), count(distinct sku_id) from analytics.mart_sales_daily{where}""",
                parameters,
            ).fetchone()
        return {
            "date_from": str(row[0]) if row[0] is not None else None,
            "date_to": str(row[1]) if row[1] is not None else None,
            "units": int(row[2]),
            "revenue": float(row[3]),
            "average_selling_price": float(row[4]),
            "active_stores": int(row[5]),
            "active_skus": int(row[6]),
            "freshness_note": "Historical synthetic local warehouse; not live data.",
        }

    def timeseries(self, limit: int = 120, filters: AnalyticsFilters | None = None) -> list[dict[str, Any]]:
        where, parameters = self._where(filters or AnalyticsFilters())
        with self._connect() as conn:
            rows = conn.execute(
                f"""select sale_date, sum(units_sold) units, sum(net_revenue) revenue
                from analytics.mart_sales_daily{where} group by sale_date order by sale_date desc limit ?""",
                [*parameters, limit],
            ).fetchall()
        return [{"date": str(d), "units": int(u), "revenue": float(r)} for d, u, r in reversed(rows)]

    def breakdown(self, dimension: str, limit: int = 20, filters: AnalyticsFilters | None = None) -> list[dict[str, Any]]:
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
        where, parameters = self._where(filters or AnalyticsFilters())
        query = f"""select {column}, sum(units_sold) units, sum(net_revenue) revenue
            from analytics.mart_sales_daily{where} group by {column} order by revenue desc limit ?"""
        with self._connect() as conn:
            rows = conn.execute(query, [*parameters, limit]).fetchall()
        return [
            {"key": str(key), "units": int(units), "revenue": float(revenue)} for key, units, revenue in rows
        ]
