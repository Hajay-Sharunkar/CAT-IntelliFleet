from fastapi import APIRouter, Depends, HTTPException, status

from ai.provider import AIProvider, get_default_provider
from schemas.ai import (
    ForecastAIRequest,
    ForecastAIResponse,
    RecommendationAIRequest,
    RecommendationAIResponse,
    SummaryAIRequest,
    SummaryAIResponse,
)
from services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


def get_ai_provider() -> AIProvider:
    """Dependency that supplies the active AI provider (mock for now)."""
    return get_default_provider()


@router.post("/forecast", response_model=ForecastAIResponse)
def create_forecast(
    request: ForecastAIRequest,
    provider: AIProvider = Depends(get_ai_provider),
) -> ForecastAIResponse:
    try:
        return ai_service.run_forecast(request, provider)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate forecast: {error}",
        ) from error


@router.post("/recommendations", response_model=RecommendationAIResponse)
def create_recommendations(
    request: RecommendationAIRequest,
    provider: AIProvider = Depends(get_ai_provider),
) -> RecommendationAIResponse:
    try:
        return ai_service.run_recommendations(request, provider)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {error}",
        ) from error


@router.post("/summary", response_model=SummaryAIResponse)
def create_summary(
    request: SummaryAIRequest,
    provider: AIProvider = Depends(get_ai_provider),
) -> SummaryAIResponse:
    try:
        return ai_service.run_summary(request, provider)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {error}",
        ) from error
