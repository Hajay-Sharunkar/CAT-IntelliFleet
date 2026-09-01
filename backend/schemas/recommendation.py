from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecommendationCreate(BaseModel):
    asset_id: int
    recommendation_type: str = Field(..., max_length=50)
    reason: str
    confidence_score: float
    estimated_cost_saving: float | None = None
    recommendation_time: datetime | None = None
    recommendation_status: str = Field(..., max_length=30)


class RecommendationUpdate(BaseModel):
    asset_id: int | None = None
    recommendation_type: str | None = Field(None, max_length=50)
    reason: str | None = None
    confidence_score: float | None = None
    estimated_cost_saving: float | None = None
    recommendation_time: datetime | None = None
    recommendation_status: str | None = Field(None, max_length=30)


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: int
    asset_id: int
    recommendation_type: str
    reason: str
    confidence_score: float
    estimated_cost_saving: float | None
    recommendation_time: datetime
    recommendation_status: str
