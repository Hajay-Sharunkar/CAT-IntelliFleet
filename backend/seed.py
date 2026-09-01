"""Database initialization and demo seed script for CAT IntelliFleet.

Usage:
    python seed.py

Creates all tables and populates demo data only when the database is empty.
"""

from __future__ import annotations

import random
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select

import models  # noqa: F401 — register ORM models with Base.metadata
from database.database import Base, SessionLocal, engine
from models.alert import Alert
from models.asset import Asset
from models.maintenance import Maintenance
from models.operator import Operator
from models.recommendation import Recommendation
from models.rental import Rental
from models.site import Site
from models.telemetry import Telemetry

RNG = random.Random(42)
NOW = datetime.now(timezone.utc)

MACHINE_SPECS = [
    ("excavator", "336", "CAT 336 Excavator"),
    ("excavator", "352", "CAT 352 Excavator"),
    ("wheel_loader", "980", "CAT 980 Wheel Loader"),
    ("wheel_loader", "966", "CAT 966 Wheel Loader"),
    ("dozer", "D6", "CAT D6 Dozer"),
    ("dozer", "D8T", "CAT D8T Dozer"),
    ("motor_grader", "140", "CAT 140 Motor Grader"),
    ("haul_truck", "777", "CAT 777 Haul Truck"),
    ("backhoe_loader", "420", "CAT 420 Backhoe Loader"),
    ("articulated_truck", "740", "CAT 740 Articulated Truck"),
    ("compactor", "826", "CAT 826 Compactor"),
]

RENTAL_STATUSES = ["available", "rented", "overdue", "reserved", "returned"]
CURRENT_STATUSES = ["operational", "idle", "maintenance", "down", "in_transit"]
EXPERIENCE_LEVELS = ["trainee", "intermediate", "senior", "expert"]
AVAILABILITY_STATUSES = ["available", "on_duty", "off_duty", "unavailable"]
ENGINE_STATUSES = ["on", "off", "idle", "fault"]


def create_tables() -> None:
    """Create all database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


def database_is_empty(session) -> bool:
    """Return True when core tables contain no seed data."""
    site_count = session.scalar(select(func.count()).select_from(Site)) or 0
    return site_count == 0


def seed_sites(session) -> list[Site]:
    site_data = [
        ("North Ridge Quarry", "12 Quarry Road, North Ridge", 34.0522, -118.2437, "Sarah Mitchell", "active"),
        ("East Valley Construction", "88 Builder Ave, East Valley", 33.4484, -112.0740, "James Carter", "active"),
        ("River Bend Mining", "5 River Bend Hwy, Mesa", 33.4152, -111.8315, "Elena Rodriguez", "active"),
        ("Summit Highway Project", "200 Summit Pkwy, Flagstaff", 35.1983, -111.6513, "David Kim", "active"),
        ("Harbor Logistics Yard", "44 Dock Street, Long Beach", 33.7701, -118.1937, "Priya Nair", "planned"),
    ]

    sites: list[Site] = []
    for name, address, lat, lon, manager, status in site_data:
        sites.append(
            Site(
                site_name=name,
                address=address,
                latitude=lat,
                longitude=lon,
                manager_name=manager,
                status=status,
            )
        )

    session.add_all(sites)
    session.flush()
    return sites


def seed_operators(session, sites: list[Site]) -> list[Operator]:
    first_names = [
        "John", "Maria", "Ahmed", "Chen", "Liam", "Sofia", "Noah", "Aisha",
        "Ethan", "Olivia", "Raj", "Emma", "Carlos", "Grace", "Tyler",
    ]
    certifications = [
        "Excavator Class A",
        "Wheel Loader Certified",
        "Dozer Operations",
        "Haul Truck License",
        "Motor Grader Specialist",
        None,
    ]

    operators: list[Operator] = []
    for index, first_name in enumerate(first_names):
        site = sites[index % len(sites)]
        operators.append(
            Operator(
                operator_name=f"{first_name} {['Reed', 'Lopez', 'Patel', 'Nguyen', 'Brooks'][index % 5]}",
                phone=f"+1-555-{1000 + index:04d}",
                experience_level=RNG.choice(EXPERIENCE_LEVELS),
                certification=RNG.choice(certifications),
                assigned_site=site.site_id,
                availability_status=RNG.choice(AVAILABILITY_STATUSES),
            )
        )

    session.add_all(operators)
    session.flush()
    return operators


def seed_assets(session, sites: list[Site], operators: list[Operator]) -> list[Asset]:
    assets: list[Asset] = []

    for index in range(25):
        machine_type, model, base_name = MACHINE_SPECS[index % len(MACHINE_SPECS)]
        rental_status = RENTAL_STATUSES[index % len(RENTAL_STATUSES)]
        current_status = CURRENT_STATUSES[index % len(CURRENT_STATUSES)]

        site = sites[index % len(sites)] if rental_status in ("rented", "overdue", "reserved") else None
        operator = None
        if rental_status in ("rented", "overdue") and index % 4 != 0:
            operator = operators[index % len(operators)]
            operator.availability_status = "on_duty"

        created_at = NOW - timedelta(days=RNG.randint(120, 900))
        assets.append(
            Asset(
                serial_number=f"CAT-{model.replace(' ', '')}-{index + 1:03d}",
                machine_name=f"{base_name} #{index + 1}",
                machine_type=machine_type,
                manufacturer="Caterpillar",
                model=model,
                manufacturing_year=RNG.randint(2016, 2024),
                current_status=current_status,
                rental_status=rental_status,
                current_site_id=site.site_id if site else None,
                current_operator_id=operator.operator_id if operator else None,
                created_at=created_at,
                updated_at=NOW - timedelta(hours=RNG.randint(1, 72)),
            )
        )

    session.add_all(assets)
    session.flush()
    return assets


def seed_rentals(session, assets: list[Asset], sites: list[Site], operators: list[Operator]) -> list[Rental]:
    rentals: list[Rental] = []
    rental_statuses = ["active", "active", "active", "extended", "overdue", "returned", "returned", "cancelled"]

    for index in range(20):
        asset = assets[index % len(assets)]
        site = sites[index % len(sites)]
        operator = operators[index % len(operators)] if index % 5 != 0 else None
        status = rental_statuses[index % len(rental_statuses)]

        checkout_time = NOW - timedelta(days=RNG.randint(3, 45), hours=RNG.randint(0, 12))
        expected_return = checkout_time + timedelta(days=RNG.randint(7, 30))
        actual_return = None

        if status == "returned":
            actual_return = checkout_time + timedelta(days=RNG.randint(5, 20))
        elif status == "overdue":
            expected_return = NOW - timedelta(days=RNG.randint(1, 5))

        rentals.append(
            Rental(
                asset_id=asset.asset_id,
                site_id=site.site_id,
                operator_id=operator.operator_id if operator else None,
                checkout_time=checkout_time,
                expected_return=expected_return,
                actual_return=actual_return,
                rental_status=status,
            )
        )

    session.add_all(rentals)
    session.flush()
    return rentals


def seed_telemetry(session, assets: list[Asset], sites: list[Site]) -> list[Telemetry]:
    telemetry_records: list[Telemetry] = []
    records_per_asset = 300 // len(assets)
    remainder = 300 % len(assets)
    telemetry_id = 1

    for asset_index, asset in enumerate(assets):
        count = records_per_asset + (1 if asset_index < remainder else 0)
        site = next((s for s in sites if s.site_id == asset.current_site_id), sites[asset_index % len(sites)])

        base_lat = site.latitude or 33.45
        base_lon = site.longitude or -112.07
        engine_hours = Decimal(str(RNG.uniform(800, 4200)))
        idle_hours = Decimal(str(RNG.uniform(50, 600)))
        runtime_hours = max(engine_hours - idle_hours, Decimal("0"))

        for reading_index in range(count):
            days_ago = RNG.randint(0, 30)
            hours_ago = RNG.randint(0, 23)
            timestamp = NOW - timedelta(days=days_ago, hours=hours_ago, minutes=RNG.randint(0, 59))

            engine_increment = Decimal(str(round(RNG.uniform(0.2, 2.5), 2)))
            idle_increment = Decimal(str(round(RNG.uniform(0.0, 1.2), 2)))
            engine_hours += engine_increment
            idle_hours += idle_increment
            runtime_hours = max(engine_hours - idle_hours, Decimal("0"))

            telemetry_records.append(
                Telemetry(
                    telemetry_id=telemetry_id,
                    asset_id=asset.asset_id,
                    timestamp=timestamp,
                    engine_hours=engine_hours,
                    idle_hours=idle_hours,
                    runtime_hours=runtime_hours,
                    fuel_level=Decimal(str(round(RNG.uniform(8, 98), 2))),
                    latitude=base_lat + RNG.uniform(-0.02, 0.02),
                    longitude=base_lon + RNG.uniform(-0.02, 0.02),
                    engine_status=RNG.choice(ENGINE_STATUSES),
                )
            )
            telemetry_id += 1

    session.add_all(telemetry_records)
    session.flush()
    return telemetry_records


def seed_maintenance(session, assets: list[Asset]) -> list[Maintenance]:
    maintenance_types = ["preventive", "corrective", "inspection", "overhaul", "recall"]
    priorities = ["low", "medium", "high", "critical"]
    statuses = ["open", "scheduled", "in_progress", "completed", "deferred", "cancelled"]
    technicians = ["Mike Turner", "Lisa Huang", "Tom Bradley", "Nina Alvarez", None]

    records: list[Maintenance] = []
    for index in range(15):
        status = statuses[index % len(statuses)]
        scheduled = date.today() + timedelta(days=RNG.randint(-10, 20))
        completed = None
        if status == "completed":
            completed = scheduled + timedelta(days=RNG.randint(0, 3))

        records.append(
            Maintenance(
                asset_id=assets[index % len(assets)].asset_id,
                maintenance_type=maintenance_types[index % len(maintenance_types)],
                issue_description=(
                    f"Scheduled service interval review for asset unit {index + 1}. "
                    f"Inspect hydraulics, filters, and undercarriage wear."
                ),
                priority=priorities[index % len(priorities)],
                status=status,
                scheduled_date=scheduled,
                completed_date=completed,
                technician=technicians[index % len(technicians)],
                estimated_hours=Decimal(str(round(RNG.uniform(2, 16), 2))),
                remarks="Demo maintenance record." if status == "completed" else None,
            )
        )

    session.add_all(records)
    session.flush()
    return records


def seed_alerts(session, assets: list[Asset]) -> list[Alert]:
    alert_specs = [
        ("excess_idle", "warning", "open", "Idle hours exceeded threshold in the last monitoring window."),
        ("missing_operator", "high", "open", "Rented asset has no operator assigned."),
        ("overdue_rental", "critical", "open", "Rental is past expected return date."),
        ("maintenance_due", "high", "acknowledged", "Preventive maintenance is due this week."),
        ("low_fuel", "warning", "open", "Fuel level dropped below operational threshold."),
        ("engine_fault", "critical", "open", "Telemetry reported an engine fault code."),
        ("geofence_deviation", "warning", "resolved", "Machine GPS is outside assigned site boundary."),
        ("excess_idle", "info", "dismissed", "Short idle spike detected during lunch break."),
        ("low_fuel", "high", "open", "Fuel level critically low; refuel required."),
        ("overdue_rental", "high", "acknowledged", "Site manager notified about overdue return."),
    ]

    alerts: list[Alert] = []
    for index, (alert_type, severity, status, description) in enumerate(alert_specs):
        generated = NOW - timedelta(days=RNG.randint(0, 14), hours=RNG.randint(1, 20))
        resolved = None
        if status in ("resolved", "dismissed"):
            resolved = generated + timedelta(hours=RNG.randint(2, 48))

        alerts.append(
            Alert(
                asset_id=assets[index % len(assets)].asset_id,
                alert_type=alert_type,
                severity=severity,
                description=description,
                status=status,
                generated_time=generated,
                resolved_time=resolved,
            )
        )

    session.add_all(alerts)
    session.flush()
    return alerts


def seed_recommendations(session, assets: list[Asset]) -> list[Recommendation]:
    recommendation_specs = [
        ("move_machine", "High idle time at current site; demand rising at River Bend Mining.", 0.8700, 18500.00, "pending"),
        ("return_machine", "Asset underutilized for 9 days; return to yard to reduce cost.", 0.7900, 9200.00, "pending"),
        ("assign_operator", "Rented excavator has no operator assigned.", 0.9100, None, "pending"),
        ("extend_rental", "Site utilization is strong; extend rental through next phase.", 0.8300, 6400.00, "accepted"),
        ("maintenance_required", "Engine hours approaching next preventive service interval.", 0.8800, 7300.00, "pending"),
        ("move_machine", "Loader needed at Summit Highway Project within 48 hours.", 0.7600, 11200.00, "rejected"),
        ("return_machine", "Overdue rental should be closed and asset reassigned.", 0.8400, 5100.00, "expired"),
        ("maintenance_required", "Corrective maintenance recommended due to fault alerts.", 0.8000, 9800.00, "executed"),
    ]

    recommendations: list[Recommendation] = []
    for index, (rec_type, reason, confidence, saving, status) in enumerate(recommendation_specs):
        recommendations.append(
            Recommendation(
                asset_id=assets[index % len(assets)].asset_id,
                recommendation_type=rec_type,
                reason=reason,
                confidence_score=Decimal(str(confidence)),
                estimated_cost_saving=Decimal(str(saving)) if saving is not None else None,
                recommendation_time=NOW - timedelta(days=RNG.randint(0, 10), hours=RNG.randint(1, 12)),
                recommendation_status=status,
            )
        )

    session.add_all(recommendations)
    session.flush()
    return recommendations


def sync_asset_rental_states(
    session,
    assets: list[Asset],
    rentals: list[Rental],
    operators: list[Operator],
) -> None:
    """Align asset rental pointers with the latest rental per asset."""
    asset_map = {asset.asset_id: asset for asset in assets}
    operator_map = {operator.operator_id: operator for operator in operators}

    latest_rental_by_asset: dict[int, Rental] = {}
    for rental in rentals:
        current = latest_rental_by_asset.get(rental.asset_id)
        if current is None or rental.checkout_time > current.checkout_time:
            latest_rental_by_asset[rental.asset_id] = rental

    for asset in assets:
        asset.current_site_id = None
        asset.current_operator_id = None
        asset.rental_status = "available"

    for rental in latest_rental_by_asset.values():
        asset = asset_map[rental.asset_id]
        if rental.actual_return is None and rental.rental_status in ("active", "extended", "overdue"):
            asset.rental_status = "overdue" if rental.rental_status == "overdue" else "rented"
            asset.current_site_id = rental.site_id
            asset.current_operator_id = rental.operator_id
            if rental.operator_id is not None:
                operator = operator_map.get(rental.operator_id)
                if operator is not None:
                    operator.availability_status = "on_duty"
        elif rental.rental_status == "returned":
            asset.rental_status = "available"


def seed_database(session) -> dict[str, int]:
    """Populate all demo tables and return inserted record counts."""
    sites = seed_sites(session)
    operators = seed_operators(session, sites)
    assets = seed_assets(session, sites, operators)
    rentals = seed_rentals(session, assets, sites, operators)
    sync_asset_rental_states(session, assets, rentals, operators)
    telemetry_records = seed_telemetry(session, assets, sites)
    maintenance_records = seed_maintenance(session, assets)
    alerts = seed_alerts(session, assets)
    recommendations = seed_recommendations(session, assets)

    session.commit()

    return {
        "sites": len(sites),
        "operators": len(operators),
        "assets": len(assets),
        "rentals": len(rentals),
        "telemetry": len(telemetry_records),
        "maintenance": len(maintenance_records),
        "alerts": len(alerts),
        "recommendations": len(recommendations),
    }


def main() -> int:
    print("CAT IntelliFleet — database seed")
    print(f"Database URL: {engine.url}")

    create_tables()
    print("Tables created (or already exist).")

    session = SessionLocal()
    try:
        if not database_is_empty(session):
            print("Database already contains data. Skipping seed.")
            return 0

        counts = seed_database(session)
        print("Demo data seeded successfully:")
        for table_name, count in counts.items():
            print(f"  - {table_name}: {count}")
        return 0
    except Exception as error:
        session.rollback()
        print(f"Seed failed: {error}", file=sys.stderr)
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
