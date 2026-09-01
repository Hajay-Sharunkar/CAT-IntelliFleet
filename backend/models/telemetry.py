from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.asset import Asset


class Telemetry(Base):
    __tablename__ = "telemetry"
    __table_args__ = (
        Index("ix_telemetry_asset_id_timestamp", "asset_id", "timestamp"),
    )

    telemetry_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.asset_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    engine_hours: Mapped[float | None] = mapped_column(Numeric(12, 2))
    idle_hours: Mapped[float | None] = mapped_column(Numeric(12, 2))
    runtime_hours: Mapped[float | None] = mapped_column(Numeric(12, 2))
    fuel_level: Mapped[float | None] = mapped_column(Numeric(5, 2))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    engine_status: Mapped[str | None] = mapped_column(String(30))

    asset: Mapped[Asset] = relationship(back_populates="telemetry_readings")
