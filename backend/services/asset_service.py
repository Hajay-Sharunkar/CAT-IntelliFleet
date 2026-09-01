from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.asset import Asset
from schemas.asset import AssetCreate, AssetUpdate


def create_asset(db: Session, asset_in: AssetCreate) -> Asset:
    now = datetime.now(timezone.utc)
    asset = Asset(
        **asset_in.model_dump(),
        created_at=now,
        updated_at=now,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_assets(db: Session, skip: int = 0, limit: int = 100) -> list[Asset]:
    stmt = select(Asset).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_asset_by_id(db: Session, asset_id: int) -> Asset | None:
    return db.get(Asset, asset_id)


def get_asset_by_serial_number(db: Session, serial_number: str) -> Asset | None:
    stmt = select(Asset).where(Asset.serial_number == serial_number)
    return db.scalars(stmt).first()


def update_asset(db: Session, asset_id: int, asset_in: AssetUpdate) -> Asset | None:
    asset = db.get(Asset, asset_id)
    if asset is None:
        return None

    update_data = asset_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)

    asset.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, asset_id: int) -> bool:
    asset = db.get(Asset, asset_id)
    if asset is None:
        return False

    db.delete(asset)
    db.commit()
    return True
