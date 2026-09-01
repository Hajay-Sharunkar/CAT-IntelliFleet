from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.asset import Asset
    from models.operator import Operator
    from models.site import Site


class Rental(Base):
    __tablename__ = "rentals"
    __table_args__ = (
        Index("ix_rentals_asset_id_checkout_time", "asset_id", "checkout_time"),
        Index("ix_rentals_site_id_checkout_time", "site_id", "checkout_time"),
        Index("ix_rentals_rental_status", "rental_status"),
    )

    rental_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.asset_id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.site_id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    operator_id: Mapped[int | None] = mapped_column(
        ForeignKey("operators.operator_id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    checkout_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expected_return: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual_return: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rental_status: Mapped[str] = mapped_column(String(30))

    asset: Mapped[Asset] = relationship(back_populates="rentals")
    site: Mapped[Site] = relationship(back_populates="rentals")
    operator: Mapped[Operator | None] = relationship(back_populates="rentals")
