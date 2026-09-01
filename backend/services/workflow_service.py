from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.alert import Alert
from models.asset import Asset
from models.maintenance import Maintenance
from models.rental import Rental
from models.telemetry import Telemetry
from schemas.alert import AlertCreate
from schemas.workflow import AlertGenerateRequest, CheckOutRequest, TelemetryUpdateRequest
from database.sqlite_compat import assign_telemetry_primary_key
from services import (
    alert_service,
    asset_service,
    maintenance_service,
    operator_service,
    rental_service,
    site_service,
)
from services.workflow_exceptions import WorkflowError

_ACTIVE_RENTAL_STATUSES = ("active", "extended", "overdue")
_OPEN_ALERT_STATUSES = ("open", "acknowledged")
_OPEN_MAINTENANCE_STATUSES = ("open", "scheduled")

_ENGINE_STATUS_TO_ASSET_STATUS = {
    "on": "operational",
    "idle": "idle",
    "off": "idle",
    "fault": "down",
}


def _get_active_rental(db: Session, asset_id: int) -> Rental | None:
    stmt = (
        select(Rental)
        .where(
            Rental.asset_id == asset_id,
            Rental.actual_return.is_(None),
            Rental.rental_status.in_(_ACTIVE_RENTAL_STATUSES),
        )
        .order_by(Rental.checkout_time.desc())
        .limit(1)
    )
    return db.scalars(stmt).first()


def _has_open_alert(db: Session, asset_id: int, alert_type: str) -> bool:
    stmt = select(Alert).where(
        Alert.asset_id == asset_id,
        Alert.alert_type == alert_type,
        Alert.status.in_(_OPEN_ALERT_STATUSES),
    )
    return db.scalars(stmt).first() is not None


def _create_alert_if_new(db: Session, alert_in: AlertCreate) -> Alert | None:
    if _has_open_alert(db, alert_in.asset_id, alert_in.alert_type):
        return None
    return alert_service.create_alert(db, alert_in)


def check_out_equipment(db: Session, request: CheckOutRequest) -> tuple[Rental, Asset]:
    asset = asset_service.get_asset_by_id(db, request.asset_id)
    if asset is None:
        raise WorkflowError(f"Asset with id {request.asset_id} not found", 404)

    site = site_service.get_site_by_id(db, request.site_id)
    if site is None:
        raise WorkflowError(f"Site with id {request.site_id} not found", 404)

    if request.operator_id is not None:
        operator = operator_service.get_operator_by_id(db, request.operator_id)
        if operator is None:
            raise WorkflowError(f"Operator with id {request.operator_id} not found", 404)

    if _get_active_rental(db, request.asset_id) is not None:
        raise WorkflowError(
            f"Asset with id {request.asset_id} already has an active rental",
            409,
        )

    if asset.rental_status in ("rented", "overdue"):
        raise WorkflowError(
            f"Asset with id {request.asset_id} is not available for check-out",
            409,
        )

    now = datetime.now(timezone.utc)
    rental = Rental(
        asset_id=request.asset_id,
        site_id=request.site_id,
        operator_id=request.operator_id,
        checkout_time=now,
        expected_return=request.expected_return,
        rental_status="active",
    )
    db.add(rental)

    asset.rental_status = "rented"
    asset.current_site_id = request.site_id
    asset.current_operator_id = request.operator_id
    asset.updated_at = now

    if request.operator_id is not None:
        operator = operator_service.get_operator_by_id(db, request.operator_id)
        if operator is not None:
            operator.availability_status = "on_duty"

    db.commit()
    db.refresh(rental)
    db.refresh(asset)
    return rental, asset


def check_in_equipment(db: Session, asset_id: int, actual_return: datetime | None = None) -> tuple[Rental, Asset]:
    asset = asset_service.get_asset_by_id(db, asset_id)
    if asset is None:
        raise WorkflowError(f"Asset with id {asset_id} not found", 404)

    rental = _get_active_rental(db, asset_id)
    if rental is None:
        raise WorkflowError(f"No active rental found for asset with id {asset_id}", 404)

    return_time = actual_return or datetime.now(timezone.utc)
    rental.actual_return = return_time
    rental.rental_status = "returned"

    previous_operator_id = asset.current_operator_id
    asset.rental_status = "available"
    asset.current_site_id = None
    asset.current_operator_id = None
    asset.updated_at = return_time

    if previous_operator_id is not None:
        operator = operator_service.get_operator_by_id(db, previous_operator_id)
        if operator is not None:
            operator.availability_status = "available"

    db.commit()
    db.refresh(rental)
    db.refresh(asset)
    return rental, asset


def update_equipment_telemetry(
    db: Session,
    request: TelemetryUpdateRequest,
) -> tuple[Telemetry, Asset]:
    asset = asset_service.get_asset_by_id(db, request.asset_id)
    if asset is None:
        raise WorkflowError(f"Asset with id {request.asset_id} not found", 404)

    now = datetime.now(timezone.utc)
    runtime_hours = request.runtime_hours
    if runtime_hours is None and request.engine_hours is not None and request.idle_hours is not None:
        runtime_hours = max(float(request.engine_hours) - float(request.idle_hours), 0)

    telemetry = Telemetry(
        asset_id=request.asset_id,
        timestamp=now,
        engine_hours=request.engine_hours,
        idle_hours=request.idle_hours,
        runtime_hours=runtime_hours,
        fuel_level=request.fuel_level,
        latitude=request.latitude,
        longitude=request.longitude,
        engine_status=request.engine_status,
    )
    assign_telemetry_primary_key(db, telemetry)
    db.add(telemetry)

    if request.engine_status is not None:
        mapped_status = _ENGINE_STATUS_TO_ASSET_STATUS.get(request.engine_status)
        if mapped_status is not None:
            asset.current_status = mapped_status

    asset.updated_at = now
    db.commit()
    db.refresh(telemetry)
    db.refresh(asset)
    return telemetry, asset


def complete_maintenance(
    db: Session,
    maintenance_id: int,
    completed_date: date | None = None,
    remarks: str | None = None,
) -> Maintenance:
    maintenance = maintenance_service.get_maintenance_by_id(db, maintenance_id)
    if maintenance is None:
        raise WorkflowError(f"Maintenance with id {maintenance_id} not found", 404)

    if maintenance.status == "completed":
        raise WorkflowError(
            f"Maintenance with id {maintenance_id} is already completed",
            409,
        )

    maintenance.status = "completed"
    maintenance.completed_date = completed_date or date.today()
    if remarks is not None:
        maintenance.remarks = remarks

    db.commit()
    db.refresh(maintenance)
    return maintenance


def _get_latest_telemetry(db: Session, asset_id: int) -> Telemetry | None:
    stmt = (
        select(Telemetry)
        .where(Telemetry.asset_id == asset_id)
        .order_by(Telemetry.timestamp.desc())
        .limit(1)
    )
    return db.scalars(stmt).first()


def _get_previous_telemetry(db: Session, asset_id: int, before_timestamp: datetime) -> Telemetry | None:
    stmt = (
        select(Telemetry)
        .where(
            Telemetry.asset_id == asset_id,
            Telemetry.timestamp < before_timestamp,
        )
        .order_by(Telemetry.timestamp.desc())
        .limit(1)
    )
    return db.scalars(stmt).first()


def generate_alerts(db: Session, request: AlertGenerateRequest) -> list[Alert]:
    generated: list[Alert] = []
    now = datetime.now(timezone.utc)
    today = date.today()

    rentals = rental_service.get_rentals(db, skip=0, limit=10_000)
    for rental in rentals:
        if rental.actual_return is not None:
            continue

        if rental.expected_return < now or rental.rental_status == "overdue":
            alert = _create_alert_if_new(
                db,
                AlertCreate(
                    asset_id=rental.asset_id,
                    alert_type="overdue_rental",
                    severity="high",
                    description=(
                        f"Rental {rental.rental_id} is overdue. "
                        f"Expected return was {rental.expected_return.isoformat()}."
                    ),
                    status="open",
                ),
            )
            if alert is not None:
                generated.append(alert)

    assets = asset_service.get_assets(db, skip=0, limit=10_000)
    for asset in assets:
        if asset.rental_status in ("rented", "overdue") and asset.current_operator_id is None:
            alert = _create_alert_if_new(
                db,
                AlertCreate(
                    asset_id=asset.asset_id,
                    alert_type="missing_operator",
                    severity="warning",
                    description=f"Asset {asset.machine_name} is rented but has no assigned operator.",
                    status="open",
                ),
            )
            if alert is not None:
                generated.append(alert)

        latest = _get_latest_telemetry(db, asset.asset_id)
        if latest is not None:
            if latest.fuel_level is not None and latest.fuel_level < request.fuel_threshold:
                alert = _create_alert_if_new(
                    db,
                    AlertCreate(
                        asset_id=asset.asset_id,
                        alert_type="low_fuel",
                        severity="warning",
                        description=(
                            f"Fuel level at {latest.fuel_level}% "
                            f"is below threshold of {request.fuel_threshold}%."
                        ),
                        status="open",
                    ),
                )
                if alert is not None:
                    generated.append(alert)

            if latest.idle_hours is not None:
                previous = _get_previous_telemetry(db, asset.asset_id, latest.timestamp)
                if previous is not None and previous.idle_hours is not None:
                    idle_delta = float(latest.idle_hours) - float(previous.idle_hours)
                    if idle_delta > request.idle_hours_threshold:
                        alert = _create_alert_if_new(
                            db,
                            AlertCreate(
                                asset_id=asset.asset_id,
                                alert_type="excess_idle",
                                severity="warning",
                                description=(
                                    f"Idle hours increased by {idle_delta:.2f} "
                                    f"(threshold: {request.idle_hours_threshold})."
                                ),
                                status="open",
                            ),
                        )
                        if alert is not None:
                            generated.append(alert)

    maintenance_records = maintenance_service.get_maintenance_records(db, skip=0, limit=10_000)
    for record in maintenance_records:
        if record.status not in _OPEN_MAINTENANCE_STATUSES:
            continue

        if record.scheduled_date is not None and record.scheduled_date <= today:
            alert = _create_alert_if_new(
                db,
                AlertCreate(
                    asset_id=record.asset_id,
                    alert_type="maintenance_due",
                    severity="high",
                    description=(
                        f"Maintenance {record.maintenance_id} "
                        f"({record.maintenance_type}) is due on {record.scheduled_date}."
                    ),
                    status="open",
                ),
            )
            if alert is not None:
                generated.append(alert)

    return generated
