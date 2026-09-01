from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.recommendation import Recommendation


class DecisionLog(Base):
    __tablename__ = "decision_log"
    __table_args__ = (
        Index("ix_decision_log_recommendation_id", "recommendation_id"),
        Index("ix_decision_log_decision_time", "decision_time"),
    )

    decision_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("recommendations.recommendation_id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    manager_name: Mapped[str] = mapped_column(String(150))
    action_taken: Mapped[str] = mapped_column(String(50))
    decision_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    remarks: Mapped[str | None] = mapped_column(Text)

    recommendation: Mapped[Recommendation] = relationship(back_populates="decisions")
