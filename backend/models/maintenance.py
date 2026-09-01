from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.asset import Asset


class Maintenance(Base):
    __tablename__ = "maintenance"
    __table_args__ = (
        Index("ix_maintenance_asset_id_scheduled_date", "asset_id", "scheduled_date"),
        Index("ix_maintenance_status_priority", "status", "priority"),
    )

    maintenance_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.asset_id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    maintenance_type: Mapped[str] = mapped_column(String(50))
    issue_description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(30))
    scheduled_date: Mapped[date | None] = mapped_column(Date)
    completed_date: Mapped[date | None] = mapped_column(Date)
    technician: Mapped[str | None] = mapped_column(String(150))
    estimated_hours: Mapped[float | None] = mapped_column(Numeric(8, 2))
    remarks: Mapped[str | None] = mapped_column(Text)

    asset: Mapped[Asset] = relationship(back_populates="maintenance_records")
