from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.asset import AssetCreate, AssetResponse, AssetUpdate
from services import asset_service
from services.qr_service import generate_qr_png, get_qr_payload

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetResponse])
def list_assets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[AssetResponse]:
    return asset_service.get_assets(db, skip=skip, limit=limit)


@router.get("/{asset_id}/qr")
def get_asset_qr(asset_id: int, db: Session = Depends(get_db)) -> Response:
    asset = asset_service.get_asset_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found",
        )

    png_bytes = generate_qr_png(get_qr_payload(asset))
    return Response(content=png_bytes, media_type="image/png")


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)) -> AssetResponse:
    asset = asset_service.get_asset_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found",
        )
    return asset


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset_in: AssetCreate,
    db: Session = Depends(get_db),
) -> AssetResponse:
    return asset_service.create_asset(db, asset_in)


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    asset_in: AssetUpdate,
    db: Session = Depends(get_db),
) -> AssetResponse:
    asset = asset_service.update_asset(db, asset_id, asset_in)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found",
        )
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)) -> None:
    deleted = asset_service.delete_asset(db, asset_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found",
        )
