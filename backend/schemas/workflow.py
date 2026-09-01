from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from schemas.alert import AlertResponse
from schemas.asset import AssetResponse
from schemas.maintenance import MaintenanceResponse
from schemas.rental import RentalResponse
from schemas.telemetry import TelemetryResponse


class CheckOutRequest(BaseModel):
    asset_id: int
    site_id: int
    operator_id: int | None = None
    expected_return: datetime


class CheckOutResponse(BaseModel):
    rental: RentalResponse
    asset: AssetResponse


class CheckInRequest(BaseModel):
    asset_id: int
    actual_return: datetime | None = None


class CheckInResponse(BaseModel):
    rental: RentalResponse
    asset: AssetResponse


class TelemetryUpdateRequest(BaseModel):
    asset_id: int
    engine_hours: float | None = None
    idle_hours: float | None = None
    runtime_hours: float | None = None
    fuel_level: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    engine_status: str | None = Field(None, max_length=30)


class TelemetryUpdateResponse(BaseModel):
    telemetry: TelemetryResponse
    asset: AssetResponse


class MaintenanceCompleteRequest(BaseModel):
    completed_date: date | None = None
    remarks: str | None = None


class MaintenanceCompleteResponse(BaseModel):
    maintenance: MaintenanceResponse


class AlertGenerateRequest(BaseModel):
    idle_hours_threshold: float = Field(4.0, ge=0)
    fuel_threshold: float = Field(15.0, ge=0, le=100)


class AlertGenerateResponse(BaseModel):
    generated_count: int
    alerts: list[AlertResponse]


class ScanRequest(BaseModel):
    qr_data: str = Field(..., min_length=1)


class ScanResponse(BaseModel):
    asset_id: int
    serial_number: str
    machine_name: str
    status: str
    current_site: str | None
    current_operator: str | None
    next_action: Literal["check_out", "check_in"]
