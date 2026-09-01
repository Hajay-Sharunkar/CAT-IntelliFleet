from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.alert import Alert
from models.asset import Asset
from models.maintenance import Maintenance
from models.rental import Rental
from models.site import Site
from models.telemetry import Telemetry
from schemas.analytics import (
    AlertAnalyticsResponse,
    CriticalFuelAsset,
    FuelAnalyticsResponse,
    MachineTypeDistributionItem,
    MaintenanceAnalyticsResponse,
    RentalAnalyticsResponse,
    SitePerformanceItem,
    UtilizationTrendItem,
)

_ACTIVE_RENTAL_STATUSES = ("active", "extended", "overdue")
_OPEN_ALERT_STATUSES = ("open", "acknowledged")
_OPEN_MAINTENANCE_STATUSES = ("open", "scheduled")
_LOW_FUEL_THRESHOLD = 15.0
_CRITICAL_FUEL_THRESHOLD = 10.0
_DEFAULT_TREND_DAYS = 30

_ALERT_TYPE_LABELS = {
    "excess_idle": "idle",
    "low_fuel": "fuel",
    "maintenance_due": "maintenance",
    "overdue_rental": "overdue",
    "missing_operator": "missing_operator",
    "engine_fault": "engine_fault",
    "geofence_deviation": "geofence",
}


def _to_float(value: object | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _format_machine_type(value: str) -> str:
    return value.replace("_", " ").title()


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


def get_utilization_trend(db: Session, days: int = _DEFAULT_TREND_DAYS) -> list[UtilizationTrendItem]:
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = (
        select(Telemetry)
        .where(Telemetry.timestamp >= start_date)
        .order_by(Telemetry.timestamp.asc())
    )
    readings = db.scalars(stmt).all()
    if not readings:
        return []

    daily_utilization: dict[date, list[float]] = defaultdict(list)
    daily_idle: dict[date, list[float]] = defaultdict(list)

    for reading in readings:
        reading_date = reading.timestamp.date()
        utilization, idle_pct = _calc_utilization_percentages(
            _to_float(reading.engine_hours),
            _to_float(reading.idle_hours),
        )
        if utilization is not None:
            daily_utilization[reading_date].append(utilization)
        if idle_pct is not None:
            daily_idle[reading_date].append(idle_pct)

    trend: list[UtilizationTrendItem] = []
    for day in sorted(daily_utilization.keys()):
        util_values = daily_utilization[day]
        idle_values = daily_idle.get(day, [])
        trend.append(
            UtilizationTrendItem(
                date=day,
                average_utilization=round(sum(util_values) / len(util_values), 2) if util_values else 0.0,
                average_idle=round(sum(idle_values) / len(idle_values), 2) if idle_values else 0.0,
            )
        )

    return trend


def get_machine_type_distribution(db: Session) -> list[MachineTypeDistributionItem]:
    stmt = (
        select(Asset.machine_type, func.count(Asset.asset_id).label("count"))
        .group_by(Asset.machine_type)
        .order_by(func.count(Asset.asset_id).desc())
    )
    rows = db.execute(stmt).all()

    return [
        MachineTypeDistributionItem(
            machine_type=_format_machine_type(machine_type),
            count=count,
        )
        for machine_type, count in rows
    ]


def get_rental_analytics(db: Session) -> RentalAnalyticsResponse:
    now = datetime.now(timezone.utc)

    active = db.scalar(
        select(func.count())
        .select_from(Rental)
        .where(
            Rental.actual_return.is_(None),
            Rental.rental_status.in_(_ACTIVE_RENTAL_STATUSES),
        )
    ) or 0

    completed = db.scalar(
        select(func.count())
        .select_from(Rental)
        .where(Rental.rental_status == "returned")
    ) or 0

    overdue = db.scalar(
        select(func.count())
        .select_from(Rental)
        .where(
            Rental.actual_return.is_(None),
            Rental.rental_status.in_(("overdue", "active", "extended")),
            Rental.expected_return < now,
        )
    ) or 0

    completed_rentals = db.scalars(
        select(Rental).where(
            Rental.rental_status == "returned",
            Rental.actual_return.is_not(None),
        )
    ).all()

    durations: list[float] = []
    for rental in completed_rentals:
        checkout = rental.checkout_time
        actual_return = rental.actual_return
        if checkout is None or actual_return is None:
            continue
        if checkout.tzinfo is None:
            checkout = checkout.replace(tzinfo=timezone.utc)
        if actual_return.tzinfo is None:
            actual_return = actual_return.replace(tzinfo=timezone.utc)
        durations.append((actual_return - checkout).total_seconds() / 3600)

    average_duration_hours = round(sum(durations) / len(durations), 2) if durations else 0.0

    return RentalAnalyticsResponse(
        active=active,
        completed=completed,
        overdue=overdue,
        average_duration_hours=average_duration_hours,
    )


def get_fuel_analytics(db: Session) -> FuelAnalyticsResponse:
    telemetry_map = _get_latest_telemetry_by_asset(db)
    if not telemetry_map:
        return FuelAnalyticsResponse(
            average_fuel=0.0,
            low_fuel_assets=0,
            critical_assets=[],
        )

    assets = db.scalars(
        select(Asset).where(Asset.asset_id.in_(telemetry_map.keys())).order_by(Asset.asset_id)
    ).all()
    asset_map = {asset.asset_id: asset for asset in assets}

    fuel_levels: list[float] = []
    low_fuel_count = 0
    critical_assets: list[CriticalFuelAsset] = []

    for asset_id, reading in telemetry_map.items():
        fuel = _to_float(reading.fuel_level)
        if fuel is None:
            continue

        fuel_levels.append(fuel)
        if fuel < _LOW_FUEL_THRESHOLD:
            low_fuel_count += 1

        if fuel < _CRITICAL_FUEL_THRESHOLD:
            asset = asset_map.get(asset_id)
            if asset is not None:
                critical_assets.append(
                    CriticalFuelAsset(
                        asset_id=asset.asset_id,
                        asset_code=asset.serial_number,
                        machine_name=asset.machine_name,
                        fuel_level=round(fuel, 2),
                    )
                )

    average_fuel = round(sum(fuel_levels) / len(fuel_levels), 2) if fuel_levels else 0.0
    critical_assets.sort(key=lambda item: item.fuel_level)

    return FuelAnalyticsResponse(
        average_fuel=average_fuel,
        low_fuel_assets=low_fuel_count,
        critical_assets=critical_assets,
    )


def get_maintenance_analytics(db: Session) -> MaintenanceAnalyticsResponse:
    today = date.today()

    completed = db.scalar(
        select(func.count()).select_from(Maintenance).where(Maintenance.status == "completed")
    ) or 0

    scheduled = db.scalar(
        select(func.count())
        .select_from(Maintenance)
        .where(Maintenance.status.in_(_OPEN_MAINTENANCE_STATUSES))
    ) or 0

    overdue = db.scalar(
        select(func.count())
        .select_from(Maintenance)
        .where(
            Maintenance.status.in_(_OPEN_MAINTENANCE_STATUSES),
            Maintenance.scheduled_date.is_not(None),
            Maintenance.scheduled_date < today,
        )
    ) or 0

    completed_records = db.scalars(
        select(Maintenance).where(
            Maintenance.status == "completed",
            Maintenance.scheduled_date.is_not(None),
            Maintenance.completed_date.is_not(None),
        )
    ).all()

    completion_days = [
        (record.completed_date - record.scheduled_date).days
        for record in completed_records
        if record.completed_date is not None and record.scheduled_date is not None
    ]
    average_completion_days = (
        round(sum(completion_days) / len(completion_days), 2) if completion_days else 0.0
    )

    return MaintenanceAnalyticsResponse(
        completed=completed,
        scheduled=scheduled,
        overdue=overdue,
        average_completion_days=average_completion_days,
    )


def get_alert_analytics(db: Session) -> AlertAnalyticsResponse:
    alerts = db.scalars(
        select(Alert).where(Alert.status.in_(_OPEN_ALERT_STATUSES))
    ).all()

    by_type: dict[str, int] = defaultdict(int)
    for alert in alerts:
        label = _ALERT_TYPE_LABELS.get(alert.alert_type, alert.alert_type)
        by_type[label] += 1

    return AlertAnalyticsResponse(
        total_open=len(alerts),
        by_type=dict(by_type),
    )


def get_site_performance(db: Session) -> list[SitePerformanceItem]:
    sites = db.scalars(select(Site).order_by(Site.site_name)).all()
    if not sites:
        return []

    telemetry_map = _get_latest_telemetry_by_asset(db)

    asset_counts = dict(
        db.execute(
            select(Asset.current_site_id, func.count(Asset.asset_id))
            .where(Asset.current_site_id.is_not(None))
            .group_by(Asset.current_site_id)
        ).all()
    )

    rental_counts = dict(
        db.execute(
            select(Rental.site_id, func.count(Rental.rental_id))
            .where(
                Rental.actual_return.is_(None),
                Rental.rental_status.in_(_ACTIVE_RENTAL_STATUSES),
            )
            .group_by(Rental.site_id)
        ).all()
    )

    assets_by_site: dict[int, list[Asset]] = defaultdict(list)
    site_assets = db.scalars(
        select(Asset).where(Asset.current_site_id.is_not(None))
    ).all()
    for asset in site_assets:
        if asset.current_site_id is not None:
            assets_by_site[asset.current_site_id].append(asset)

    performance: list[SitePerformanceItem] = []
    for site in sites:
        site_asset_list = assets_by_site.get(site.site_id, [])
        utilization_values: list[float] = []

        for asset in site_asset_list:
            reading = telemetry_map.get(asset.asset_id)
            if reading is None:
                continue
            utilization, _ = _calc_utilization_percentages(
                _to_float(reading.engine_hours),
                _to_float(reading.idle_hours),
            )
            if utilization is not None:
                utilization_values.append(utilization)

        avg_utilization = (
            round(sum(utilization_values) / len(utilization_values), 2)
            if utilization_values
            else 0.0
        )

        performance.append(
            SitePerformanceItem(
                site=site.site_name,
                assets=asset_counts.get(site.site_id, 0),
                average_utilization=avg_utilization,
                active_rentals=rental_counts.get(site.site_id, 0),
            )
        )

    return performance
