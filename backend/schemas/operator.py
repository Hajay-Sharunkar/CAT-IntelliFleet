from pydantic import BaseModel, ConfigDict, Field


class OperatorCreate(BaseModel):
    operator_name: str = Field(..., max_length=150)
    phone: str | None = Field(None, max_length=30)
    experience_level: str = Field(..., max_length=30)
    certification: str | None = Field(None, max_length=150)
    assigned_site: int | None = None
    availability_status: str = Field(..., max_length=30)


class OperatorUpdate(BaseModel):
    operator_name: str | None = Field(None, max_length=150)
    phone: str | None = Field(None, max_length=30)
    experience_level: str | None = Field(None, max_length=30)
    certification: str | None = Field(None, max_length=150)
    assigned_site: int | None = None
    availability_status: str | None = Field(None, max_length=30)


class OperatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operator_id: int
    operator_name: str
    phone: str | None
    experience_level: str
    certification: str | None
    assigned_site: int | None
    availability_status: str
