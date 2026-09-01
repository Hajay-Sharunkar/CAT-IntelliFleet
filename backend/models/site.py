from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from models.asset import Asset
    from models.operator import Operator
    from models.rental import Rental


class Site(Base):
    __tablename__ = "sites"
    __table_args__ = (Index("ix_sites_status", "status"),)

    site_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_name: Mapped[str] = mapped_column(String(150), unique=True)
    address: Mapped[str | None] = mapped_column(String(500))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    manager_name: Mapped[str | None] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(30))

    operators: Mapped[list[Operator]] = relationship(
        back_populates="site",
        foreign_keys="Operator.assigned_site",
    )
    assets: Mapped[list[Asset]] = relationship(
        back_populates="current_site",
        foreign_keys="Asset.current_site_id",
    )
    rentals: Mapped[list[Rental]] = relationship(back_populates="site")
