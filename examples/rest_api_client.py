"""Minimal client for the repository's existing FastAPI routes."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


FORECAST_ROW = {
    "lag_1": 0.0,
    "lag_7": 4.0,
    "lag_14": 4.0,
    "lag_28": 0.0,
    "sales_velocity_7d": 14.0,
    "rolling_mean_7d": 2.0,
    "rolling_std_7d": 2.0,
    "scheduled_selling_price": 3.83,
    "store_id": 10,
    "sku_id": 39,
    "region_id": 2,
    "brand_name": "Orchard",
    "category_name": "Juice",
    "store_type": "convenience",
    "channel": "modern_trade",
}

STOCKOUT_ROW = {
    "stock_quantity": 71,
    "reserved_quantity": 0,
    "available_quantity": 71,
    "reorder_point": 73,
    "safety_stock": 26,
    "distance_to_reorder_point": -2,
    "replenishment_sum_7d": 136,
    "stock_to_safety_ratio": 2.7307692308,
    "sales_velocity_7d": 5.5625,
    "warehouse_id": 3,
    "sku_id": 6,
}

SEGMENT_ROW = {
    "store_id": 10,
    "revenue_30d": 6476.38,
    "average_price_30d": 2.6411111111,
    "promotion_unit_share_30d": 0.1648393195,
    "revenue_volatility_30d": 5.6237946816,
}


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def request(
        self, method: str, path: str, payload: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = self.base_url + path
        if query:
            url += "?" + urlencode(query, doseq=True)
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            url,
            data=body,
            method=method,
            headers={"Content-Type": "application/json", "X-Request-ID": "usage-showcase"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8")
            raise RuntimeError(f"API returned HTTP {exc.code}: {detail}") from exc


def run_showcase(base_url: str) -> dict[str, Any]:
    client = ApiClient(base_url)
    return {
        "health": client.request("GET", "/health"),
        "readiness": client.request("GET", "/ready"),
        "forecast": client.request("POST", "/api/v1/predict/forecast", {"rows": [FORECAST_ROW]}),
        "stockout": client.request("POST", "/api/v1/predict/stockout", {"rows": [STOCKOUT_ROW]}),
        "segment_membership": client.request(
            "POST", "/api/v1/analytics/segments/assign", {"rows": [SEGMENT_ROW]}
        ),
        "anomaly_candidates": client.request(
            "GET", "/api/v1/analytics/anomalies", query={"offset": 2, "limit": 1}
        ),
        "basket_rules": client.request(
            "GET", "/api/v1/analytics/basket-rules", query={"limit": 2}
        ),
        "promotion_summary": client.request(
            "GET", "/api/v1/analytics/promotions", query={"offset": 1, "limit": 1}
        ),
        "bi_summary": client.request("GET", "/api/v1/bi/summary"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url", default=os.getenv("FSI_BASE_URL", "http://127.0.0.1:8000")
    )
    args = parser.parse_args()
    print(json.dumps(run_showcase(args.base_url), indent=2, default=str))


if __name__ == "__main__":
    main()
