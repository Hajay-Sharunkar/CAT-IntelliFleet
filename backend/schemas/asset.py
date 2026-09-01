from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssetCreate(BaseModel):
    serial_number: str = Field(..., max_length=80)
    machine_name: str = Field(..., max_length=150)
    machine_type: str = Field(..., max_length=80)
    manufacturer: str = Field(..., max_length=80)
    model: str = Field(..., max_length=80)
    manufacturing_year: int | None = None
    current_status: str = Field(..., max_length=30)
    rental_status: str = Field(..., max_length=30)
    current_site_id: int | None = None
    current_operator_id: int | None = None


class AssetUpdate(BaseModel):
    serial_number: str | None = Field(None, max_length=80)
    machine_name: str | None = Field(None, max_length=150)
    machine_type: str | None = Field(None, max_length=80)
    manufacturer: str | None = Field(None, max_length=80)
    model: str | None = Field(None, max_length=80)
    manufacturing_year: int | None = None
    current_status: str | None = Field(None, max_length=30)
    rental_status: str | None = Field(None, max_length=30)
    current_site_id: int | None = None
    current_operator_id: int | None = None


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: int
    serial_number: str
    machine_name: str
    machine_type: str
    manufacturer: str
    model: str
    manufacturing_year: int | None
    current_status: str
    rental_status: str
    current_site_id: int | None
    current_operator_id: int | None
    created_at: datetime
    updated_at: datetime
