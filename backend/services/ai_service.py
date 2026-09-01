from ai.forecast import ForecastRequest, generate_forecast
from ai.provider import AIProvider
from ai.recommendation import RecommendationAIRequest as AIRecommendationRequest
from ai.recommendation import generate_recommendations
from ai.summary import SummaryRequest, generate_summary
from schemas.ai import (
    ForecastAIRequest,
    ForecastAIResponse,
    RecommendationAIItemResponse,
    RecommendationAIRequest,
    RecommendationAIResponse,
    SummaryAIRequest,
    SummaryAIResponse,
)


def run_forecast(request: ForecastAIRequest, provider: AIProvider) -> ForecastAIResponse:
    """Execute a fleet forecast via the AI abstraction layer."""
    ai_request = ForecastRequest(
        context=request.context,
        horizon_days=request.horizon_days,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    result = generate_forecast(ai_request, provider=provider)

    return ForecastAIResponse(
        summary=result.summary,
        horizon_days=result.horizon_days,
        confidence=result.confidence,
        provider=result.provider,
        model=result.model,
        is_mock=result.is_mock,
        details=result.details,
    )


def run_recommendations(
    request: RecommendationAIRequest,
    provider: AIProvider,
) -> RecommendationAIResponse:
    """Execute fleet recommendations via the AI abstraction layer."""
    ai_request = AIRecommendationRequest(
        context=request.context,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    result = generate_recommendations(ai_request, provider=provider)

    return RecommendationAIResponse(
        recommendations=[
            RecommendationAIItemResponse(
                recommendation_type=item.recommendation_type,
                reason=item.reason,
                confidence_score=item.confidence_score,
                estimated_cost_saving=item.estimated_cost_saving,
            )
            for item in result.recommendations
        ],
        provider=result.provider,
        model=result.model,
        is_mock=result.is_mock,
        raw_summary=result.raw_summary,
        details=result.details,
    )


def run_summary(request: SummaryAIRequest, provider: AIProvider) -> SummaryAIResponse:
    """Execute a dashboard summary via the AI abstraction layer."""
    ai_request = SummaryRequest(
        context=request.context,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    result = generate_summary(ai_request, provider=provider)

    return SummaryAIResponse(
        summary=result.summary,
        highlights=result.highlights,
        provider=result.provider,
        model=result.model,
        is_mock=result.is_mock,
        details=result.details,
    )
