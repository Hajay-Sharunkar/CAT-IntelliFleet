from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.telemetry import TelemetryCreate, TelemetryResponse, TelemetryUpdate
from services import telemetry_service

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.get("", response_model=list[TelemetryResponse])
def list_telemetry(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[TelemetryResponse]:
    return telemetry_service.get_telemetry(db, skip=skip, limit=limit)


@router.get("/{telemetry_id}", response_model=TelemetryResponse)
def get_telemetry(telemetry_id: int, db: Session = Depends(get_db)) -> TelemetryResponse:
    telemetry = telemetry_service.get_telemetry_by_id(db, telemetry_id)
    if telemetry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telemetry with id {telemetry_id} not found",
        )
    return telemetry


@router.post("", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
def create_telemetry(
    telemetry_in: TelemetryCreate,
    db: Session = Depends(get_db),
) -> TelemetryResponse:
    return telemetry_service.create_telemetry(db, telemetry_in)


@router.put("/{telemetry_id}", response_model=TelemetryResponse)
def update_telemetry(
    telemetry_id: int,
    telemetry_in: TelemetryUpdate,
    db: Session = Depends(get_db),
) -> TelemetryResponse:
    telemetry = telemetry_service.update_telemetry(db, telemetry_id, telemetry_in)
    if telemetry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telemetry with id {telemetry_id} not found",
        )
    return telemetry


@router.delete("/{telemetry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_telemetry(telemetry_id: int, db: Session = Depends(get_db)) -> None:
    deleted = telemetry_service.delete_telemetry(db, telemetry_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telemetry with id {telemetry_id} not found",
        )
