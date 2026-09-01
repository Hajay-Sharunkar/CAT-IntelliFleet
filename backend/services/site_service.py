from sqlalchemy import select
from sqlalchemy.orm import Session

from models.site import Site
from schemas.site import SiteCreate, SiteUpdate


def create_site(db: Session, site_in: SiteCreate) -> Site:
    site = Site(**site_in.model_dump())
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


def get_sites(db: Session, skip: int = 0, limit: int = 100) -> list[Site]:
    stmt = select(Site).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_site_by_id(db: Session, site_id: int) -> Site | None:
    return db.get(Site, site_id)


def update_site(db: Session, site_id: int, site_in: SiteUpdate) -> Site | None:
    site = db.get(Site, site_id)
    if site is None:
        return None

    update_data = site_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(site, field, value)

    db.commit()
    db.refresh(site)
    return site


def delete_site(db: Session, site_id: int) -> bool:
    site = db.get(Site, site_id)
    if site is None:
        return False

    db.delete(site)
    db.commit()
    return True
