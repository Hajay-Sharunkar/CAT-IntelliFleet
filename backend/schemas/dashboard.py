from datetime import date, datetime

from pydantic import BaseModel, Field


class DashboardOverviewResponse(BaseModel):
    total_assets: int
    available_assets: int
    rented_assets: int
    maintenance_assets: int
    idle_assets: int
    active_rentals: int
    open_alerts: int
    pending_recommendations: int


class FleetDashboardItem(BaseModel):
    asset_id: int
    asset_code: str
    machine_type: str
    model: str
    status: str
    current_site: str | None
    operator: str | None
    fuel_level: float | None
    engine_hours: float | None
    idle_hours: float | None
    last_update: datetime | None


class AlertDashboardItem(BaseModel):
    alert_id: int
    asset_id: int
    asset: str
    alert_type: str
    severity: str
    created_time: datetime
    status: str


class MaintenanceDashboardItem(BaseModel):
    maintenance_id: int
    asset_id: int
    asset_code: str
    machine_name: str
    machine_type: str
    model: str
    maintenance_type: str
    priority: str
    status: str
    scheduled_date: date | None
    completed_date: date | None
    technician: str | None


class MaintenanceDashboardResponse(BaseModel):
    upcoming: list[MaintenanceDashboardItem]
    in_progress: list[MaintenanceDashboardItem]
    completed_today: list[MaintenanceDashboardItem]
    overdue: list[MaintenanceDashboardItem]


class RentalDashboardItem(BaseModel):
    rental_id: int
    asset_id: int
    asset_code: str
    machine_name: str
    site_name: str
    operator: str | None
    checkout_time: datetime
    expected_return: datetime
    rental_status: str
    duration_hours: float


class UtilizationDashboardItem(BaseModel):
    asset_id: int
    asset_code: str
    machine_name: str
    engine_hours: float | None
    idle_hours: float | None
    utilization_percentage: float | None
    idle_percentage: float | None
    rental_status: str
    current_site: str | None


class DashboardSearchParams(BaseModel):
    asset_code: str | None = None
    machine_type: str | None = None
    status: str | None = None
    site: str | None = None
