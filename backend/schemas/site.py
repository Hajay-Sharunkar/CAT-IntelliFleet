from pydantic import BaseModel, ConfigDict, Field


class SiteCreate(BaseModel):
    site_name: str = Field(..., max_length=150)
    address: str | None = Field(None, max_length=500)
    latitude: float | None = None
    longitude: float | None = None
    manager_name: str | None = Field(None, max_length=150)
    status: str = Field(..., max_length=30)


class SiteUpdate(BaseModel):
    site_name: str | None = Field(None, max_length=150)
    address: str | None = Field(None, max_length=500)
    latitude: float | None = None
    longitude: float | None = None
    manager_name: str | None = Field(None, max_length=150)
    status: str | None = Field(None, max_length=30)


class SiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    site_id: int
    site_name: str
    address: str | None
    latitude: float | None
    longitude: float | None
    manager_name: str | None
    status: str
