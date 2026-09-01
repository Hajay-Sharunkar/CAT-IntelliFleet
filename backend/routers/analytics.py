from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.analytics import (
    AlertAnalyticsResponse,
    FuelAnalyticsResponse,
    MachineTypeDistributionItem,
    MaintenanceAnalyticsResponse,
    RentalAnalyticsResponse,
    SitePerformanceItem,
    UtilizationTrendItem,
)
from services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/utilization-trend", response_model=list[UtilizationTrendItem])
def get_utilization_trend(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> list[UtilizationTrendItem]:
    return analytics_service.get_utilization_trend(db, days=days)


@router.get("/machine-types", response_model=list[MachineTypeDistributionItem])
def get_machine_type_distribution(
    db: Session = Depends(get_db),
) -> list[MachineTypeDistributionItem]:
    return analytics_service.get_machine_type_distribution(db)


@router.get("/rentals", response_model=RentalAnalyticsResponse)
def get_rental_analytics(db: Session = Depends(get_db)) -> RentalAnalyticsResponse:
    return analytics_service.get_rental_analytics(db)


@router.get("/fuel", response_model=FuelAnalyticsResponse)
def get_fuel_analytics(db: Session = Depends(get_db)) -> FuelAnalyticsResponse:
    return analytics_service.get_fuel_analytics(db)


@router.get("/maintenance", response_model=MaintenanceAnalyticsResponse)
def get_maintenance_analytics(db: Session = Depends(get_db)) -> MaintenanceAnalyticsResponse:
    return analytics_service.get_maintenance_analytics(db)


@router.get("/alerts", response_model=AlertAnalyticsResponse)
def get_alert_analytics(db: Session = Depends(get_db)) -> AlertAnalyticsResponse:
    return analytics_service.get_alert_analytics(db)


@router.get("/sites", response_model=list[SitePerformanceItem])
def get_site_performance(db: Session = Depends(get_db)) -> list[SitePerformanceItem]:
    return analytics_service.get_site_performance(db)
