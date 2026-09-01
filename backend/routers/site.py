from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.site import SiteCreate, SiteResponse, SiteUpdate
from services import site_service

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=list[SiteResponse])
def list_sites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[SiteResponse]:
    return site_service.get_sites(db, skip=skip, limit=limit)


@router.get("/{site_id}", response_model=SiteResponse)
def get_site(site_id: int, db: Session = Depends(get_db)) -> SiteResponse:
    site = site_service.get_site_by_id(db, site_id)
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with id {site_id} not found",
        )
    return site


@router.post("", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
def create_site(
    site_in: SiteCreate,
    db: Session = Depends(get_db),
) -> SiteResponse:
    return site_service.create_site(db, site_in)


@router.put("/{site_id}", response_model=SiteResponse)
def update_site(
    site_id: int,
    site_in: SiteUpdate,
    db: Session = Depends(get_db),
) -> SiteResponse:
    site = site_service.update_site(db, site_id, site_in)
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with id {site_id} not found",
        )
    return site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(site_id: int, db: Session = Depends(get_db)) -> None:
    deleted = site_service.delete_site(db, site_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with id {site_id} not found",
        )
