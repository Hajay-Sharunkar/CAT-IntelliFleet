from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.alert import Alert
    from models.maintenance import Maintenance
    from models.operator import Operator
    from models.recommendation import Recommendation
    from models.rental import Rental
    from models.site import Site
    from models.telemetry import Telemetry


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (
        Index("ix_assets_current_site_id", "current_site_id"),
        Index("ix_assets_current_status", "current_status"),
        Index("ix_assets_rental_status", "rental_status"),
        Index("ix_assets_machine_type", "machine_type"),
    )

    asset_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    serial_number: Mapped[str] = mapped_column(String(80), unique=True)
    machine_name: Mapped[str] = mapped_column(String(150))
    machine_type: Mapped[str] = mapped_column(String(80))
    manufacturer: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(80))
    manufacturing_year: Mapped[int | None] = mapped_column(Integer)
    current_status: Mapped[str] = mapped_column(String(30))
    rental_status: Mapped[str] = mapped_column(String(30))
    current_site_id: Mapped[int | None] = mapped_column(
        ForeignKey("sites.site_id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    current_operator_id: Mapped[int | None] = mapped_column(
        ForeignKey("operators.operator_id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    current_site: Mapped[Site | None] = relationship(
        back_populates="assets",
        foreign_keys=[current_site_id],
    )
    current_operator: Mapped[Operator | None] = relationship(
        back_populates="assets",
        foreign_keys=[current_operator_id],
    )
    rentals: Mapped[list[Rental]] = relationship(back_populates="asset")
    telemetry_readings: Mapped[list[Telemetry]] = relationship(back_populates="asset")
    maintenance_records: Mapped[list[Maintenance]] = relationship(back_populates="asset")
    alerts: Mapped[list[Alert]] = relationship(back_populates="asset")
    recommendations: Mapped[list[Recommendation]] = relationship(back_populates="asset")
