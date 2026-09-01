from typing import Any

from pydantic import BaseModel, Field


class ForecastAIRequest(BaseModel):
    context: str = Field(..., min_length=1, description="Fleet data context passed to the AI layer")
    horizon_days: int = Field(30, ge=1, le=365)
    temperature: float = Field(0.4, ge=0.0, le=2.0)
    max_tokens: int = Field(1200, ge=1, le=8192)


class ForecastAIResponse(BaseModel):
    summary: str
    horizon_days: int
    confidence: float
    provider: str
    model: str
    is_mock: bool
    details: dict[str, Any] = Field(default_factory=dict)


class RecommendationAIRequest(BaseModel):
    context: str = Field(..., min_length=1, description="Fleet data context passed to the AI layer")
    temperature: float = Field(0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(1500, ge=1, le=8192)


class RecommendationAIItemResponse(BaseModel):
    recommendation_type: str
    reason: str
    confidence_score: float
    estimated_cost_saving: float | None = None


class RecommendationAIResponse(BaseModel):
    recommendations: list[RecommendationAIItemResponse]
    provider: str
    model: str
    is_mock: bool
    raw_summary: str
    details: dict[str, Any] = Field(default_factory=dict)


class SummaryAIRequest(BaseModel):
    context: str = Field(..., min_length=1, description="Dashboard data context passed to the AI layer")
    temperature: float = Field(0.5, ge=0.0, le=2.0)
    max_tokens: int = Field(1000, ge=1, le=8192)


class SummaryAIResponse(BaseModel):
    summary: str
    highlights: list[str]
    provider: str
    model: str
    is_mock: bool
    details: dict[str, Any] = Field(default_factory=dict)
