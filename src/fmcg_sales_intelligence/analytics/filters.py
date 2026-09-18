from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AnalyticsFilters(BaseModel):
    """Bounded, typed filters supported by the sales analytical mart."""

    model_config = ConfigDict(extra="forbid")
    date_from: date | None = None
    date_to: date | None = None
    regions: list[int] = Field(default_factory=list, max_length=50)
    channels: list[str] = Field(default_factory=list, max_length=20)
    stores: list[int] = Field(default_factory=list, max_length=100)
    categories: list[str] = Field(default_factory=list, max_length=100)
    brands: list[str] = Field(default_factory=list, max_length=100)
    skus: list[int] = Field(default_factory=list, max_length=200)
    promotion: bool | None = None

    def validate_range(self) -> "AnalyticsFilters":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must not be later than date_to")
        return self
