"""Fleet forecast request preparation for the AI layer.

This module assembles forecast prompts and returns mock responses.
No database access or business rules are implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ai.prompts import build_fleet_forecast_prompt
from ai.provider import AICompletionRequest, AIProvider, get_default_provider


@dataclass(frozen=True)
class ForecastRequest:
    """Input payload for a fleet forecast AI request."""

    context: str
    horizon_days: int = 30
    temperature: float = 0.4
    max_tokens: int = 1200
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ForecastResponse:
    """Normalized forecast response returned to callers."""

    summary: str
    horizon_days: int
    confidence: float
    provider: str
    model: str
    is_mock: bool = True
    details: dict[str, Any] = field(default_factory=dict)


def prepare_forecast_request(request: ForecastRequest) -> AICompletionRequest:
    """Build a provider-ready completion request for fleet forecasting."""
    system_prompt, user_prompt = build_fleet_forecast_prompt(
        context=request.context,
        horizon_days=request.horizon_days,
    )

    return AICompletionRequest(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        metadata={"task_type": "fleet_forecast", **request.metadata},
    )


def generate_forecast(
    request: ForecastRequest,
    provider: AIProvider | None = None,
) -> ForecastResponse:
    """Prepare and execute a fleet forecast request.

    Currently returns a mock response via ``MockAIProvider``.
    """
    ai_provider = provider or get_default_provider()
    completion_request = prepare_forecast_request(request)
    completion_response = ai_provider.complete(completion_request)

    return ForecastResponse(
        summary=completion_response.content,
        horizon_days=request.horizon_days,
        confidence=0.75,
        provider=completion_response.provider,
        model=completion_response.model,
        is_mock=completion_response.raw.get("mock", False),
        details={
            "usage": completion_response.usage,
            "metadata": completion_request.metadata,
        },
    )
