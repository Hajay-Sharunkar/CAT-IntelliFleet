from datetime import date

from pydantic import BaseModel, Field


class UtilizationTrendItem(BaseModel):
    date: date
    average_utilization: float
    average_idle: float


class MachineTypeDistributionItem(BaseModel):
    machine_type: str
    count: int


class RentalAnalyticsResponse(BaseModel):
    active: int
    completed: int
    overdue: int
    average_duration_hours: float


class CriticalFuelAsset(BaseModel):
    asset_id: int
    asset_code: str
    machine_name: str
    fuel_level: float


class FuelAnalyticsResponse(BaseModel):
    average_fuel: float
    low_fuel_assets: int
    critical_assets: list[CriticalFuelAsset]


class MaintenanceAnalyticsResponse(BaseModel):
    completed: int
    scheduled: int
    overdue: int
    average_completion_days: float


class AlertAnalyticsResponse(BaseModel):
    total_open: int
    by_type: dict[str, int]


class SitePerformanceItem(BaseModel):
    site: str
    assets: int
    average_utilization: float
    active_rentals: int
