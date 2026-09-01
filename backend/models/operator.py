from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.asset import Asset
    from models.rental import Rental
    from models.site import Site


class Operator(Base):
    __tablename__ = "operators"
    __table_args__ = (
        Index("ix_operators_assigned_site_availability_status", "assigned_site", "availability_status"),
        Index("ix_operators_assigned_site", "assigned_site"),
    )

    operator_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operator_name: Mapped[str] = mapped_column(String(150))
    phone: Mapped[str | None] = mapped_column(String(30))
    experience_level: Mapped[str] = mapped_column(String(30))
    certification: Mapped[str | None] = mapped_column(String(150))
    assigned_site: Mapped[int | None] = mapped_column(
        ForeignKey("sites.site_id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    availability_status: Mapped[str] = mapped_column(String(30))

    site: Mapped[Site | None] = relationship(
        back_populates="operators",
        foreign_keys=[assigned_site],
    )
    assets: Mapped[list[Asset]] = relationship(
        back_populates="current_operator",
        foreign_keys="Asset.current_operator_id",
    )
    rentals: Mapped[list[Rental]] = relationship(back_populates="operator")
