from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.dashboard import (
    AlertDashboardItem,
    DashboardOverviewResponse,
    FleetDashboardItem,
    MaintenanceDashboardResponse,
    RentalDashboardItem,
    UtilizationDashboardItem,
)
from services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(db: Session = Depends(get_db)) -> DashboardOverviewResponse:
    return dashboard_service.get_overview(db)


@router.get("/fleet", response_model=list[FleetDashboardItem])
def get_fleet_dashboard(db: Session = Depends(get_db)) -> list[FleetDashboardItem]:
    return dashboard_service.get_fleet_dashboard(db)


@router.get("/alerts", response_model=list[AlertDashboardItem])
def get_alerts_dashboard(db: Session = Depends(get_db)) -> list[AlertDashboardItem]:
    return dashboard_service.get_alerts_dashboard(db)


@router.get("/maintenance", response_model=MaintenanceDashboardResponse)
def get_maintenance_dashboard(db: Session = Depends(get_db)) -> MaintenanceDashboardResponse:
    return dashboard_service.get_maintenance_dashboard(db)


@router.get("/rentals", response_model=list[RentalDashboardItem])
def get_rentals_dashboard(db: Session = Depends(get_db)) -> list[RentalDashboardItem]:
    return dashboard_service.get_rentals_dashboard(db)


@router.get("/utilization", response_model=list[UtilizationDashboardItem])
def get_utilization_dashboard(db: Session = Depends(get_db)) -> list[UtilizationDashboardItem]:
    return dashboard_service.get_utilization_dashboard(db)


@router.get("/search", response_model=list[FleetDashboardItem])
def search_dashboard(
    asset_code: str | None = Query(None),
    machine_type: str | None = Query(None),
    status: str | None = Query(None),
    site: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[FleetDashboardItem]:
    return dashboard_service.search_fleet(
        db,
        asset_code=asset_code,
        machine_type=machine_type,
        status=status,
        site=site,
    )
