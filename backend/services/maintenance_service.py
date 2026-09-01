from sqlalchemy import select
from sqlalchemy.orm import Session

from models.maintenance import Maintenance
from schemas.maintenance import MaintenanceCreate, MaintenanceUpdate


def create_maintenance(db: Session, maintenance_in: MaintenanceCreate) -> Maintenance:
    maintenance = Maintenance(**maintenance_in.model_dump())
    db.add(maintenance)
    db.commit()
    db.refresh(maintenance)
    return maintenance


def get_maintenance_records(db: Session, skip: int = 0, limit: int = 100) -> list[Maintenance]:
    stmt = select(Maintenance).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_maintenance_by_id(db: Session, maintenance_id: int) -> Maintenance | None:
    return db.get(Maintenance, maintenance_id)


def update_maintenance(
    db: Session,
    maintenance_id: int,
    maintenance_in: MaintenanceUpdate,
) -> Maintenance | None:
    maintenance = db.get(Maintenance, maintenance_id)
    if maintenance is None:
        return None

    update_data = maintenance_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(maintenance, field, value)

    db.commit()
    db.refresh(maintenance)
    return maintenance


def delete_maintenance(db: Session, maintenance_id: int) -> bool:
    maintenance = db.get(Maintenance, maintenance_id)
    if maintenance is None:
        return False

    db.delete(maintenance)
    db.commit()
    return True
