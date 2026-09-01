from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.rental import RentalCreate, RentalResponse, RentalUpdate
from services import rental_service

router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.get("", response_model=list[RentalResponse])
def list_rentals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[RentalResponse]:
    return rental_service.get_rentals(db, skip=skip, limit=limit)


@router.get("/{rental_id}", response_model=RentalResponse)
def get_rental(rental_id: int, db: Session = Depends(get_db)) -> RentalResponse:
    rental = rental_service.get_rental_by_id(db, rental_id)
    if rental is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with id {rental_id} not found",
        )
    return rental


@router.post("", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
def create_rental(
    rental_in: RentalCreate,
    db: Session = Depends(get_db),
) -> RentalResponse:
    return rental_service.create_rental(db, rental_in)


@router.put("/{rental_id}", response_model=RentalResponse)
def update_rental(
    rental_id: int,
    rental_in: RentalUpdate,
    db: Session = Depends(get_db),
) -> RentalResponse:
    rental = rental_service.update_rental(db, rental_id, rental_in)
    if rental is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with id {rental_id} not found",
        )
    return rental


@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rental(rental_id: int, db: Session = Depends(get_db)) -> None:
    deleted = rental_service.delete_rental(db, rental_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with id {rental_id} not found",
        )
