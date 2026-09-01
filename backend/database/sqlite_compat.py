"""SQLite compatibility helpers for CAT IntelliFleet.

SQLite only auto-increments INTEGER primary keys. The telemetry table uses
BIGINT, so inserts must assign ``telemetry_id`` explicitly when using SQLite.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from config.settings import settings
from models.telemetry import Telemetry


def assign_telemetry_primary_key(db: Session, telemetry: Telemetry) -> None:
    """Assign the next telemetry_id when running on SQLite."""
    if not settings.database_url.startswith("sqlite"):
        return

    if telemetry.telemetry_id is not None:
        return

    next_id = db.scalar(select(func.coalesce(func.max(Telemetry.telemetry_id), 0) + 1))
    telemetry.telemetry_id = int(next_id or 1)
