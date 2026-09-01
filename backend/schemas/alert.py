from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AlertCreate(BaseModel):
    asset_id: int
    alert_type: str = Field(..., max_length=50)
    severity: str = Field(..., max_length=20)
    description: str
    status: str = Field(..., max_length=30)
    generated_time: datetime | None = None
    resolved_time: datetime | None = None


class AlertUpdate(BaseModel):
    asset_id: int | None = None
    alert_type: str | None = Field(None, max_length=50)
    severity: str | None = Field(None, max_length=20)
    description: str | None = None
    status: str | None = Field(None, max_length=30)
    generated_time: datetime | None = None
    resolved_time: datetime | None = None


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alert_id: int
    asset_id: int
    alert_type: str
    severity: str
    description: str
    status: str
    generated_time: datetime
    resolved_time: datetime | None
