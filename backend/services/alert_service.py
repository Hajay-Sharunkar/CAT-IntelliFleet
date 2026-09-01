from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.alert import Alert
from schemas.alert import AlertCreate, AlertUpdate


def create_alert(db: Session, alert_in: AlertCreate) -> Alert:
    alert_data = alert_in.model_dump()
    if alert_data.get("generated_time") is None:
        alert_data["generated_time"] = datetime.now(timezone.utc)

    alert = Alert(**alert_data)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alerts(db: Session, skip: int = 0, limit: int = 100) -> list[Alert]:
    stmt = select(Alert).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_alert_by_id(db: Session, alert_id: int) -> Alert | None:
    return db.get(Alert, alert_id)


def update_alert(db: Session, alert_id: int, alert_in: AlertUpdate) -> Alert | None:
    alert = db.get(Alert, alert_id)
    if alert is None:
        return None

    update_data = alert_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)

    db.commit()
    db.refresh(alert)
    return alert


def delete_alert(db: Session, alert_id: int) -> bool:
    alert = db.get(Alert, alert_id)
    if alert is None:
        return False

    db.delete(alert)
    db.commit()
    return True
