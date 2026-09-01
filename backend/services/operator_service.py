from sqlalchemy import select
from sqlalchemy.orm import Session

from models.operator import Operator
from schemas.operator import OperatorCreate, OperatorUpdate


def create_operator(db: Session, operator_in: OperatorCreate) -> Operator:
    operator = Operator(**operator_in.model_dump())
    db.add(operator)
    db.commit()
    db.refresh(operator)
    return operator


def get_operators(db: Session, skip: int = 0, limit: int = 100) -> list[Operator]:
    stmt = select(Operator).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_operator_by_id(db: Session, operator_id: int) -> Operator | None:
    return db.get(Operator, operator_id)


def update_operator(db: Session, operator_id: int, operator_in: OperatorUpdate) -> Operator | None:
    operator = db.get(Operator, operator_id)
    if operator is None:
        return None

    update_data = operator_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(operator, field, value)

    db.commit()
    db.refresh(operator)
    return operator


def delete_operator(db: Session, operator_id: int) -> bool:
    operator = db.get(Operator, operator_id)
    if operator is None:
        return False

    db.delete(operator)
    db.commit()
    return True
