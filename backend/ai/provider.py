"""AI provider abstraction for CAT IntelliFleet.

This module defines the provider interface and a mock implementation.
Live integrations (Groq, Gemini, Mistral) will implement ``AIProvider`` later.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AICompletionRequest:
    """Normalized request payload sent to any AI provider."""

    prompt: str
    system_prompt: str | None = None
    temperature: float = 0.7
    max_tokens: int = 1024
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AICompletionResponse:
    """Normalized response returned by any AI provider."""

    content: str
    provider: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


class AIProvider(ABC):
    """Provider contract for all LLM backends."""

    @abstractmethod
    def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        """Execute a completion request and return normalized output."""


class MockAIProvider(AIProvider):
    """Mock provider used during development before live API integration."""

    provider_name: str = "mock"
    model_name: str = "mock-model-v1"

    def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        """Return a deterministic placeholder response without calling an API."""
        task_type = request.metadata.get("task_type", "generic")
        preview = request.prompt.strip().splitlines()[0] if request.prompt.strip() else "No prompt provided"

        content = (
            f"[MOCK {task_type.upper()} RESPONSE] "
            f"Processed prompt preview: {preview[:120]}"
        )

        return AICompletionResponse(
            content=content,
            provider=self.provider_name,
            model=self.model_name,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            raw={"mock": True, "task_type": task_type},
        )


def get_default_provider() -> AIProvider:
    """Return the default provider for the current environment.

    Live provider selection (Groq, Gemini, Mistral) will be wired here later.
    """
    return MockAIProvider()
