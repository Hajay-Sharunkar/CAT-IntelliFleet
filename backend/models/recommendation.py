from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.asset import Asset
    from models.decision_log import DecisionLog


class Recommendation(Base):
    __tablename__ = "recommendations"
    __table_args__ = (
        Index("ix_recommendations_status_time", "recommendation_status", "recommendation_time"),
        Index("ix_recommendations_asset_id_time", "asset_id", "recommendation_time"),
    )

    recommendation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.asset_id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    recommendation_type: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 4))
    estimated_cost_saving: Mapped[float | None] = mapped_column(Numeric(12, 2))
    recommendation_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    recommendation_status: Mapped[str] = mapped_column(String(30))

    asset: Mapped[Asset] = relationship(back_populates="recommendations")
    decisions: Mapped[list[DecisionLog]] = relationship(back_populates="recommendation")
