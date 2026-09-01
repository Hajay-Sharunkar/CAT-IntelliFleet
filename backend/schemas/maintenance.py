from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceCreate(BaseModel):
    asset_id: int
    maintenance_type: str = Field(..., max_length=50)
    issue_description: str
    priority: str = Field(..., max_length=20)
    status: str = Field(..., max_length=30)
    scheduled_date: date | None = None
    completed_date: date | None = None
    technician: str | None = Field(None, max_length=150)
    estimated_hours: float | None = None
    remarks: str | None = None


class MaintenanceUpdate(BaseModel):
    asset_id: int | None = None
    maintenance_type: str | None = Field(None, max_length=50)
    issue_description: str | None = None
    priority: str | None = Field(None, max_length=20)
    status: str | None = Field(None, max_length=30)
    scheduled_date: date | None = None
    completed_date: date | None = None
    technician: str | None = Field(None, max_length=150)
    estimated_hours: float | None = None
    remarks: str | None = None


class MaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    maintenance_id: int
    asset_id: int
    maintenance_type: str
    issue_description: str
    priority: str
    status: str
    scheduled_date: date | None
    completed_date: date | None
    technician: str | None
    estimated_hours: float | None
    remarks: str | None
