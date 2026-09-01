from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelemetryCreate(BaseModel):
    asset_id: int
    timestamp: datetime
    engine_hours: float | None = None
    idle_hours: float | None = None
    runtime_hours: float | None = None
    fuel_level: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    engine_status: str | None = Field(None, max_length=30)


class TelemetryUpdate(BaseModel):
    asset_id: int | None = None
    timestamp: datetime | None = None
    engine_hours: float | None = None
    idle_hours: float | None = None
    runtime_hours: float | None = None
    fuel_level: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    engine_status: str | None = Field(None, max_length=30)


class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telemetry_id: int
    asset_id: int
    timestamp: datetime
    engine_hours: float | None
    idle_hours: float | None
    runtime_hours: float | None
    fuel_level: float | None
    latitude: float | None
    longitude: float | None
    engine_status: str | None
