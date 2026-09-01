"""Fleet recommendation request preparation for the AI layer.

This module assembles recommendation prompts and returns mock responses.
No database access or business rules are implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ai.prompts import build_fleet_recommendation_prompt
from ai.provider import AICompletionRequest, AIProvider, get_default_provider


@dataclass(frozen=True)
class RecommendationAIRequest:
    """Input payload for a fleet recommendation AI request."""

    context: str
    temperature: float = 0.3
    max_tokens: int = 1500
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RecommendationAIItem:
    """Single AI-generated recommendation item."""

    recommendation_type: str
    reason: str
    confidence_score: float
    estimated_cost_saving: float | None = None


@dataclass(frozen=True)
class RecommendationAIResponse:
    """Normalized recommendation response returned to callers."""

    recommendations: list[RecommendationAIItem]
    provider: str
    model: str
    is_mock: bool = True
    raw_summary: str = ""
    details: dict[str, Any] = field(default_factory=dict)


def prepare_recommendation_request(request: RecommendationAIRequest) -> AICompletionRequest:
    """Build a provider-ready completion request for fleet recommendations."""
    system_prompt, user_prompt = build_fleet_recommendation_prompt(context=request.context)

    return AICompletionRequest(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        metadata={"task_type": "fleet_recommendation", **request.metadata},
    )


def generate_recommendations(
    request: RecommendationAIRequest,
    provider: AIProvider | None = None,
) -> RecommendationAIResponse:
    """Prepare and execute a fleet recommendation request.

    Currently returns mock structured recommendations via ``MockAIProvider``.
    """
    ai_provider = provider or get_default_provider()
    completion_request = prepare_recommendation_request(request)
    completion_response = ai_provider.complete(completion_request)

    mock_items = [
        RecommendationAIItem(
            recommendation_type="move_machine",
            reason="Mock recommendation: relocate underutilized excavator to higher-demand site.",
            confidence_score=0.8200,
            estimated_cost_saving=12500.00,
        ),
        RecommendationAIItem(
            recommendation_type="maintenance_required",
            reason="Mock recommendation: preventive maintenance window approaching based on engine hours.",
            confidence_score=0.7600,
            estimated_cost_saving=4800.00,
        ),
    ]

    return RecommendationAIResponse(
        recommendations=mock_items,
        provider=completion_response.provider,
        model=completion_response.model,
        is_mock=completion_response.raw.get("mock", False),
        raw_summary=completion_response.content,
        details={
            "usage": completion_response.usage,
            "metadata": completion_request.metadata,
        },
    )
