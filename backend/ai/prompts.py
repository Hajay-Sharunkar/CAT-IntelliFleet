"""Prompt templates for CAT IntelliFleet AI tasks.

Templates are plain strings for now. Callers format them with runtime context
before passing the result to ``AIProvider.complete``.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Fleet Forecast
# ---------------------------------------------------------------------------

FLEET_FORECAST_SYSTEM_PROMPT = """You are an AI assistant for Caterpillar fleet operations.
Your role is to analyze historical fleet utilization, rental demand, and site activity
to produce concise demand and utilization forecasts.
Respond with structured, actionable insights only."""

FLEET_FORECAST_USER_TEMPLATE = """Generate a fleet forecast using the context below.

Forecast horizon: {horizon_days} days

Fleet context:
{context}

Provide:
1. Expected demand by machine type
2. Sites likely to need additional equipment
3. Risk areas (idle surplus or shortages)
4. Confidence level (0.0 to 1.0)
"""

# ---------------------------------------------------------------------------
# Fleet Recommendation
# ---------------------------------------------------------------------------

FLEET_RECOMMENDATION_SYSTEM_PROMPT = """You are an AI fleet decision assistant for Caterpillar.
Your role is to recommend operational actions such as moving machines, returning machines,
assigning operators, extending rentals, or scheduling maintenance.
Each recommendation must include a reason and an estimated confidence score."""

FLEET_RECOMMENDATION_USER_TEMPLATE = """Generate fleet recommendations using the context below.

Fleet context:
{context}

Allowed recommendation types:
- move_machine
- return_machine
- assign_operator
- extend_rental
- maintenance_required

For each recommendation include:
- recommendation_type
- reason
- confidence_score (0.0000 to 1.0000)
- estimated_cost_saving (if available)
"""

# ---------------------------------------------------------------------------
# Fleet Summary
# ---------------------------------------------------------------------------

FLEET_SUMMARY_SYSTEM_PROMPT = """You are an AI assistant summarizing Caterpillar fleet operations.
Your role is to produce an executive dashboard summary from operational metrics.
Keep the summary concise, factual, and suitable for fleet managers."""

FLEET_SUMMARY_USER_TEMPLATE = """Summarize the current fleet dashboard state using the context below.

Dashboard context:
{context}

Provide:
1. Overall fleet health
2. Key risks and alerts
3. Utilization highlights
4. Maintenance and rental priorities
5. Suggested manager focus areas for today
"""


def build_fleet_forecast_prompt(*, context: str, horizon_days: int = 30) -> tuple[str, str]:
    """Build system and user prompts for fleet forecasting."""
    user_prompt = FLEET_FORECAST_USER_TEMPLATE.format(
        horizon_days=horizon_days,
        context=context,
    )
    return FLEET_FORECAST_SYSTEM_PROMPT, user_prompt


def build_fleet_recommendation_prompt(*, context: str) -> tuple[str, str]:
    """Build system and user prompts for fleet recommendations."""
    user_prompt = FLEET_RECOMMENDATION_USER_TEMPLATE.format(context=context)
    return FLEET_RECOMMENDATION_SYSTEM_PROMPT, user_prompt


def build_fleet_summary_prompt(*, context: str) -> tuple[str, str]:
    """Build system and user prompts for dashboard summaries."""
    user_prompt = FLEET_SUMMARY_USER_TEMPLATE.format(context=context)
    return FLEET_SUMMARY_SYSTEM_PROMPT, user_prompt
