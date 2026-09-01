from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RentalCreate(BaseModel):
    asset_id: int
    site_id: int
    operator_id: int | None = None
    checkout_time: datetime
    expected_return: datetime
    actual_return: datetime | None = None
    rental_status: str = Field(..., max_length=30)


class RentalUpdate(BaseModel):
    asset_id: int | None = None
    site_id: int | None = None
    operator_id: int | None = None
    checkout_time: datetime | None = None
    expected_return: datetime | None = None
    actual_return: datetime | None = None
    rental_status: str | None = Field(None, max_length=30)


class RentalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rental_id: int
    asset_id: int
    site_id: int
    operator_id: int | None
    checkout_time: datetime
    expected_return: datetime
    actual_return: datetime | None
    rental_status: str
