from sqlalchemy import select
from sqlalchemy.orm import Session

from database.sqlite_compat import assign_telemetry_primary_key
from models.telemetry import Telemetry
from schemas.telemetry import TelemetryCreate, TelemetryUpdate


def create_telemetry(db: Session, telemetry_in: TelemetryCreate) -> Telemetry:
    telemetry = Telemetry(**telemetry_in.model_dump())
    assign_telemetry_primary_key(db, telemetry)
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)
    return telemetry


def get_telemetry(db: Session, skip: int = 0, limit: int = 100) -> list[Telemetry]:
    stmt = select(Telemetry).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_telemetry_by_id(db: Session, telemetry_id: int) -> Telemetry | None:
    return db.get(Telemetry, telemetry_id)


def update_telemetry(db: Session, telemetry_id: int, telemetry_in: TelemetryUpdate) -> Telemetry | None:
    telemetry = db.get(Telemetry, telemetry_id)
    if telemetry is None:
        return None

    update_data = telemetry_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(telemetry, field, value)

    db.commit()
    db.refresh(telemetry)
    return telemetry


def delete_telemetry(db: Session, telemetry_id: int) -> bool:
    telemetry = db.get(Telemetry, telemetry_id)
    if telemetry is None:
        return False

    db.delete(telemetry)
    db.commit()
    return True
