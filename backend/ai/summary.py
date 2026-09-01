"""Dashboard summary request preparation for the AI layer.

This module assembles executive summary prompts and returns mock responses.
No database access or business rules are implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ai.prompts import build_fleet_summary_prompt
from ai.provider import AICompletionRequest, AIProvider, get_default_provider


@dataclass(frozen=True)
class SummaryRequest:
    """Input payload for a dashboard summary AI request."""

    context: str
    temperature: float = 0.5
    max_tokens: int = 1000
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SummaryResponse:
    """Normalized dashboard summary response returned to callers."""

    summary: str
    highlights: list[str]
    provider: str
    model: str
    is_mock: bool = True
    details: dict[str, Any] = field(default_factory=dict)


def prepare_summary_request(request: SummaryRequest) -> AICompletionRequest:
    """Build a provider-ready completion request for dashboard summaries."""
    system_prompt, user_prompt = build_fleet_summary_prompt(context=request.context)

    return AICompletionRequest(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        metadata={"task_type": "fleet_summary", **request.metadata},
    )


def generate_summary(
    request: SummaryRequest,
    provider: AIProvider | None = None,
) -> SummaryResponse:
    """Prepare and execute a dashboard summary request.

    Currently returns a mock executive summary via ``MockAIProvider``.
    """
    ai_provider = provider or get_default_provider()
    completion_request = prepare_summary_request(request)
    completion_response = ai_provider.complete(completion_request)

    mock_highlights = [
        "Mock highlight: fleet utilization remains stable across active sites.",
        "Mock highlight: overdue rentals require manager review today.",
        "Mock highlight: low-fuel assets should be prioritized for refueling.",
    ]

    return SummaryResponse(
        summary=completion_response.content,
        highlights=mock_highlights,
        provider=completion_response.provider,
        model=completion_response.model,
        is_mock=completion_response.raw.get("mock", False),
        details={
            "usage": completion_response.usage,
            "metadata": completion_request.metadata,
        },
    )
