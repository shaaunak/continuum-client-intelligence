from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AnalyticsFilters(BaseModel):
    start_date: date = Field(default=date(2026, 4, 1))
    end_date: date = Field(default=date(2026, 10, 31))
    compare_start_date: Optional[date] = None
    compare_end_date: Optional[date] = None
    segment: Optional[str] = None
    team_id: Optional[str] = None
    region: Optional[str] = None
    asset_tier: Optional[str] = None


class KpiCard(BaseModel):
    key: str
    label: str
    value: float
    previous_value: Optional[float] = None
    change: Optional[float] = None
    change_unit: str  # "pp" | "days" | "count" | "%"
    unit: str  # "%" | "days" | "count"
    direction: str  # "up" | "down" | "flat"
    favorable_direction: str  # "up" | "down"
    tooltip: str
    drilldown_route: str
    numerator: Optional[int] = None
    denominator: Optional[int] = None


class SqlLineageSnippet(BaseModel):
    metric_key: str
    kpi_name: str
    business_meaning: str
    formula: str
    numerator_desc: str
    denominator_desc: str
    applied_filters: dict[str, Any]
    sql_query: str
    as_of_date: str
    limitations: str
