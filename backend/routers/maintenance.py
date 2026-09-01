from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.maintenance import MaintenanceCreate, MaintenanceResponse, MaintenanceUpdate
from services import maintenance_service

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.get("", response_model=list[MaintenanceResponse])
def list_maintenance(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[MaintenanceResponse]:
    return maintenance_service.get_maintenance_records(db, skip=skip, limit=limit)


@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
def get_maintenance(maintenance_id: int, db: Session = Depends(get_db)) -> MaintenanceResponse:
    maintenance = maintenance_service.get_maintenance_by_id(db, maintenance_id)
    if maintenance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance with id {maintenance_id} not found",
        )
    return maintenance


@router.post("", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance(
    maintenance_in: MaintenanceCreate,
    db: Session = Depends(get_db),
) -> MaintenanceResponse:
    return maintenance_service.create_maintenance(db, maintenance_in)


@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
def update_maintenance(
    maintenance_id: int,
    maintenance_in: MaintenanceUpdate,
    db: Session = Depends(get_db),
) -> MaintenanceResponse:
    maintenance = maintenance_service.update_maintenance(db, maintenance_id, maintenance_in)
    if maintenance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance with id {maintenance_id} not found",
        )
    return maintenance


@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance(maintenance_id: int, db: Session = Depends(get_db)) -> None:
    deleted = maintenance_service.delete_maintenance(db, maintenance_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance with id {maintenance_id} not found",
        )
