from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rows: list[dict[str, Any]] = Field(min_length=1, max_length=1000)


class ContractRowsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    contract_id: str
    rows: list[dict[str, Any]] = Field(min_length=1, max_length=1000)


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Any = None
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorBody


class BusinessForecastRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    store_id: int
    sku_id: int


class BusinessStockoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    warehouse_id: int
    sku_id: int


class BusinessSegmentationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    store_id: int
