from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.workflow import (
    AlertGenerateRequest,
    AlertGenerateResponse,
    CheckInRequest,
    CheckInResponse,
    CheckOutRequest,
    CheckOutResponse,
    MaintenanceCompleteRequest,
    MaintenanceCompleteResponse,
    TelemetryUpdateRequest,
    TelemetryUpdateResponse,
)
from schemas.alert import AlertResponse
from schemas.asset import AssetResponse
from schemas.maintenance import MaintenanceResponse
from schemas.rental import RentalResponse
from schemas.telemetry import TelemetryResponse
from services import workflow_service
from services.workflow_exceptions import WorkflowError

router = APIRouter(prefix="/workflows", tags=["workflows"])


def _handle_workflow_error(error: WorkflowError) -> None:
    raise HTTPException(status_code=error.status_code, detail=error.message)


@router.post("/check-out", response_model=CheckOutResponse, status_code=status.HTTP_201_CREATED)
def check_out_equipment(
    request: CheckOutRequest,
    db: Session = Depends(get_db),
) -> CheckOutResponse:
    try:
        rental, asset = workflow_service.check_out_equipment(db, request)
    except WorkflowError as error:
        _handle_workflow_error(error)
    return CheckOutResponse(
        rental=RentalResponse.model_validate(rental),
        asset=AssetResponse.model_validate(asset),
    )


@router.post("/check-in", response_model=CheckInResponse)
def check_in_equipment(
    request: CheckInRequest,
    db: Session = Depends(get_db),
) -> CheckInResponse:
    try:
        rental, asset = workflow_service.check_in_equipment(
            db,
            request.asset_id,
            request.actual_return,
        )
    except WorkflowError as error:
        _handle_workflow_error(error)
    return CheckInResponse(
        rental=RentalResponse.model_validate(rental),
        asset=AssetResponse.model_validate(asset),
    )


@router.post("/telemetry-update", response_model=TelemetryUpdateResponse, status_code=status.HTTP_201_CREATED)
def update_equipment_telemetry(
    request: TelemetryUpdateRequest,
    db: Session = Depends(get_db),
) -> TelemetryUpdateResponse:
    try:
        telemetry, asset = workflow_service.update_equipment_telemetry(db, request)
    except WorkflowError as error:
        _handle_workflow_error(error)
    return TelemetryUpdateResponse(
        telemetry=TelemetryResponse.model_validate(telemetry),
        asset=AssetResponse.model_validate(asset),
    )


@router.post("/maintenance/{maintenance_id}/complete", response_model=MaintenanceCompleteResponse)
def complete_maintenance(
    maintenance_id: int,
    request: MaintenanceCompleteRequest,
    db: Session = Depends(get_db),
) -> MaintenanceCompleteResponse:
    try:
        maintenance = workflow_service.complete_maintenance(
            db,
            maintenance_id,
            request.completed_date,
            request.remarks,
        )
    except WorkflowError as error:
        _handle_workflow_error(error)
    return MaintenanceCompleteResponse(
        maintenance=MaintenanceResponse.model_validate(maintenance),
    )


@router.post("/alerts/generate", response_model=AlertGenerateResponse)
def generate_alerts(
    request: AlertGenerateRequest,
    db: Session = Depends(get_db),
) -> AlertGenerateResponse:
    alerts = workflow_service.generate_alerts(db, request)
    return AlertGenerateResponse(
        generated_count=len(alerts),
        alerts=[AlertResponse.model_validate(alert) for alert in alerts],
    )
