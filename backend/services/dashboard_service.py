from datetime import date, datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from models.alert import Alert
from models.asset import Asset
from models.maintenance import Maintenance
from models.recommendation import Recommendation
from models.rental import Rental
from models.site import Site
from models.telemetry import Telemetry
from schemas.dashboard import (
    AlertDashboardItem,
    DashboardOverviewResponse,
    FleetDashboardItem,
    MaintenanceDashboardItem,
    MaintenanceDashboardResponse,
    RentalDashboardItem,
    UtilizationDashboardItem,
)

_ACTIVE_RENTAL_STATUSES = ("active", "extended", "overdue")
_OPEN_ALERT_STATUSES = ("open", "acknowledged")
_OPEN_MAINTENANCE_STATUSES = ("open", "scheduled")


def _to_float(value: object | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _format_status(value: str) -> str:
    return value.replace("_", " ").title()


def _get_latest_telemetry_by_asset(db: Session) -> dict[int, Telemetry]:
    latest_subq = (
        select(
            Telemetry.asset_id,
            func.max(Telemetry.timestamp).label("latest_timestamp"),
        )
        .group_by(Telemetry.asset_id)
        .subquery()
    )

    stmt = select(Telemetry).join(
        latest_subq,
        (Telemetry.asset_id == latest_subq.c.asset_id)
        & (Telemetry.timestamp == latest_subq.c.latest_timestamp),
    )
    readings = db.scalars(stmt).all()
    return {reading.asset_id: reading for reading in readings}


def _build_fleet_item(asset: Asset, telemetry: Telemetry | None) -> FleetDashboardItem:
    return FleetDashboardItem(
        asset_id=asset.asset_id,
        asset_code=asset.serial_number,
        machine_type=asset.machine_type,
        model=asset.model,
        status=_format_status(asset.rental_status),
        current_site=asset.current_site.site_name if asset.current_site else None,
        operator=asset.current_operator.operator_name if asset.current_operator else None,
        fuel_level=_to_float(telemetry.fuel_level) if telemetry else None,
        engine_hours=_to_float(telemetry.engine_hours) if telemetry else None,
        idle_hours=_to_float(telemetry.idle_hours) if telemetry else None,
        last_update=telemetry.timestamp if telemetry else asset.updated_at,
    )


def _calc_utilization_percentages(
    engine_hours: float | None,
    idle_hours: float | None,
) -> tuple[float | None, float | None]:
    if engine_hours is None and idle_hours is None:
        return None, None

    engine = float(engine_hours or 0)
    idle = float(idle_hours or 0)
    total = engine + idle
    if total == 0:
        return 0.0, 0.0

    utilization = round((engine / total) * 100, 2)
    idle_pct = round((idle / total) * 100, 2)
    return utilization, idle_pct


def get_overview(db: Session) -> DashboardOverviewResponse:
    total_assets = db.scalar(select(func.count()).select_from(Asset)) or 0
    available_assets = db.scalar(
        select(func.count()).select_from(Asset).where(Asset.rental_status == "available")
    ) or 0
    rented_assets = db.scalar(
        select(func.count()).select_from(Asset).where(Asset.rental_status == "rented")
    ) or 0
    maintenance_assets = db.scalar(
        select(func.count()).select_from(Asset).where(Asset.current_status == "maintenance")
    ) or 0
    idle_assets = db.scalar(
        select(func.count()).select_from(Asset).where(Asset.current_status == "idle")
    ) or 0
    active_rentals = db.scalar(
        select(func.count())
        .select_from(Rental)
        .where(
            Rental.actual_return.is_(None),
            Rental.rental_status.in_(_ACTIVE_RENTAL_STATUSES),
        )
    ) or 0
    open_alerts = db.scalar(
        select(func.count()).select_from(Alert).where(Alert.status.in_(_OPEN_ALERT_STATUSES))
    ) or 0
    pending_recommendations = db.scalar(
        select(func.count())
        .select_from(Recommendation)
        .where(Recommendation.recommendation_status == "pending")
    ) or 0

    return DashboardOverviewResponse(
        total_assets=total_assets,
        available_assets=available_assets,
        rented_assets=rented_assets,
        maintenance_assets=maintenance_assets,
        idle_assets=idle_assets,
        active_rentals=active_rentals,
        open_alerts=open_alerts,
        pending_recommendations=pending_recommendations,
    )


def get_fleet_dashboard(db: Session) -> list[FleetDashboardItem]:
    stmt = (
        select(Asset)
        .outerjoin(Asset.current_site)
        .outerjoin(Asset.current_operator)
        .options(joinedload(Asset.current_site), joinedload(Asset.current_operator))
        .order_by(Asset.asset_id)
    )
    assets = db.scalars(stmt).unique().all()
    if not assets:
        return []

    telemetry_map = _get_latest_telemetry_by_asset(db)
    return [_build_fleet_item(asset, telemetry_map.get(asset.asset_id)) for asset in assets]


def get_alerts_dashboard(db: Session) -> list[AlertDashboardItem]:
    stmt = (
        select(Alert)
        .join(Alert.asset)
        .options(joinedload(Alert.asset))
        .where(Alert.status.in_(_OPEN_ALERT_STATUSES))
        .order_by(Alert.generated_time.desc())
    )
    alerts = db.scalars(stmt).unique().all()

    return [
        AlertDashboardItem(
            alert_id=alert.alert_id,
            asset_id=alert.asset_id,
            asset=alert.asset.machine_name,
            alert_type=alert.alert_type,
            severity=alert.severity,
            created_time=alert.generated_time,
            status=alert.status,
        )
        for alert in alerts
    ]


def _build_maintenance_item(record: Maintenance) -> MaintenanceDashboardItem:
    asset = record.asset
    return MaintenanceDashboardItem(
        maintenance_id=record.maintenance_id,
        asset_id=record.asset_id,
        asset_code=asset.serial_number,
        machine_name=asset.machine_name,
        machine_type=asset.machine_type,
        model=asset.model,
        maintenance_type=record.maintenance_type,
        priority=record.priority,
        status=record.status,
        scheduled_date=record.scheduled_date,
        completed_date=record.completed_date,
        technician=record.technician,
    )


def get_maintenance_dashboard(db: Session) -> MaintenanceDashboardResponse:
    today = date.today()
    stmt = (
        select(Maintenance)
        .join(Maintenance.asset)
        .options(joinedload(Maintenance.asset))
        .order_by(Maintenance.scheduled_date.asc().nulls_last(), Maintenance.maintenance_id)
    )
    records = db.scalars(stmt).unique().all()

    upcoming: list[MaintenanceDashboardItem] = []
    in_progress: list[MaintenanceDashboardItem] = []
    completed_today: list[MaintenanceDashboardItem] = []
    overdue: list[MaintenanceDashboardItem] = []

    for record in records:
        item = _build_maintenance_item(record)

        if record.status == "completed" and record.completed_date == today:
            completed_today.append(item)
        elif record.status == "in_progress":
            in_progress.append(item)
        elif (
            record.status in _OPEN_MAINTENANCE_STATUSES
            and record.scheduled_date is not None
            and record.scheduled_date < today
        ):
            overdue.append(item)
        elif record.status in ("open", "scheduled") and (
            record.scheduled_date is None or record.scheduled_date >= today
        ):
            upcoming.append(item)

    return MaintenanceDashboardResponse(
        upcoming=upcoming,
        in_progress=in_progress,
        completed_today=completed_today,
        overdue=overdue,
    )


def get_rentals_dashboard(db: Session) -> list[RentalDashboardItem]:
    now = datetime.now(timezone.utc)
    stmt = (
        select(Rental)
        .join(Rental.asset)
        .join(Rental.site)
        .outerjoin(Rental.operator)
        .options(
            joinedload(Rental.asset),
            joinedload(Rental.site),
            joinedload(Rental.operator),
        )
        .where(
            Rental.actual_return.is_(None),
            Rental.rental_status.in_(_ACTIVE_RENTAL_STATUSES),
        )
        .order_by(Rental.expected_return.asc())
    )
    rentals = db.scalars(stmt).unique().all()

    items: list[RentalDashboardItem] = []
    for rental in rentals:
        checkout = rental.checkout_time
        if checkout.tzinfo is None:
            checkout = checkout.replace(tzinfo=timezone.utc)
        duration_hours = round((now - checkout).total_seconds() / 3600, 2)

        items.append(
            RentalDashboardItem(
                rental_id=rental.rental_id,
                asset_id=rental.asset_id,
                asset_code=rental.asset.serial_number,
                machine_name=rental.asset.machine_name,
                site_name=rental.site.site_name,
                operator=rental.operator.operator_name if rental.operator else None,
                checkout_time=rental.checkout_time,
                expected_return=rental.expected_return,
                rental_status=rental.rental_status,
                duration_hours=duration_hours,
            )
        )

    return items


def get_utilization_dashboard(db: Session) -> list[UtilizationDashboardItem]:
    stmt = (
        select(Asset)
        .outerjoin(Asset.current_site)
        .options(joinedload(Asset.current_site))
        .order_by(Asset.asset_id)
    )
    assets = db.scalars(stmt).unique().all()
    if not assets:
        return []

    telemetry_map = _get_latest_telemetry_by_asset(db)
    items: list[UtilizationDashboardItem] = []

    for asset in assets:
        telemetry = telemetry_map.get(asset.asset_id)
        engine_hours = _to_float(telemetry.engine_hours) if telemetry else None
        idle_hours = _to_float(telemetry.idle_hours) if telemetry else None
        utilization_pct, idle_pct = _calc_utilization_percentages(engine_hours, idle_hours)

        items.append(
            UtilizationDashboardItem(
                asset_id=asset.asset_id,
                asset_code=asset.serial_number,
                machine_name=asset.machine_name,
                engine_hours=engine_hours,
                idle_hours=idle_hours,
                utilization_percentage=utilization_pct,
                idle_percentage=idle_pct,
                rental_status=asset.rental_status,
                current_site=asset.current_site.site_name if asset.current_site else None,
            )
        )

    return items


def search_fleet(
    db: Session,
    asset_code: str | None = None,
    machine_type: str | None = None,
    status: str | None = None,
    site: str | None = None,
) -> list[FleetDashboardItem]:
    stmt = (
        select(Asset)
        .outerjoin(Asset.current_site)
        .outerjoin(Asset.current_operator)
        .options(joinedload(Asset.current_site), joinedload(Asset.current_operator))
    )

    if asset_code:
        pattern = f"%{asset_code}%"
        stmt = stmt.where(
            or_(
                Asset.serial_number.ilike(pattern),
                Asset.machine_name.ilike(pattern),
            )
        )

    if machine_type:
        stmt = stmt.where(Asset.machine_type.ilike(f"%{machine_type}%"))

    if status:
        normalized = status.lower().replace(" ", "_")
        stmt = stmt.where(
            or_(
                Asset.rental_status.ilike(f"%{normalized}%"),
                Asset.current_status.ilike(f"%{normalized}%"),
            )
        )

    if site:
        stmt = stmt.where(Site.site_name.ilike(f"%{site}%"))

    stmt = stmt.order_by(Asset.asset_id)
    assets = db.scalars(stmt).unique().all()
    if not assets:
        return []

    telemetry_map = _get_latest_telemetry_by_asset(db)
    return [_build_fleet_item(asset, telemetry_map.get(asset.asset_id)) for asset in assets]
