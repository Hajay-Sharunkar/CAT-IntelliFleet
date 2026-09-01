"""AI abstraction layer for CAT IntelliFleet."""

from ai.forecast import ForecastRequest, ForecastResponse, generate_forecast, prepare_forecast_request
from ai.provider import (
    AICompletionRequest,
    AICompletionResponse,
    AIProvider,
    MockAIProvider,
    get_default_provider,
)
from ai.recommendation import (
    RecommendationAIRequest,
    RecommendationAIResponse,
    generate_recommendations,
    prepare_recommendation_request,
)
from ai.summary import SummaryRequest, SummaryResponse, generate_summary, prepare_summary_request

__all__ = [
    "AICompletionRequest",
    "AICompletionResponse",
    "AIProvider",
    "ForecastRequest",
    "ForecastResponse",
    "MockAIProvider",
    "RecommendationAIRequest",
    "RecommendationAIResponse",
    "SummaryRequest",
    "SummaryResponse",
    "generate_forecast",
    "generate_recommendations",
    "generate_summary",
    "get_default_provider",
    "prepare_forecast_request",
    "prepare_recommendation_request",
    "prepare_summary_request",
]
