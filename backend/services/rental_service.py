from sqlalchemy import select
from sqlalchemy.orm import Session

from models.rental import Rental
from schemas.rental import RentalCreate, RentalUpdate


def create_rental(db: Session, rental_in: RentalCreate) -> Rental:
    rental = Rental(**rental_in.model_dump())
    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental


def get_rentals(db: Session, skip: int = 0, limit: int = 100) -> list[Rental]:
    stmt = select(Rental).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_rental_by_id(db: Session, rental_id: int) -> Rental | None:
    return db.get(Rental, rental_id)


def update_rental(db: Session, rental_id: int, rental_in: RentalUpdate) -> Rental | None:
    rental = db.get(Rental, rental_id)
    if rental is None:
        return None

    update_data = rental_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rental, field, value)

    db.commit()
    db.refresh(rental)
    return rental


def delete_rental(db: Session, rental_id: int) -> bool:
    rental = db.get(Rental, rental_id)
    if rental is None:
        return False

    db.delete(rental)
    db.commit()
    return True
