from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.operator import OperatorCreate, OperatorResponse, OperatorUpdate
from services import operator_service

router = APIRouter(prefix="/operators", tags=["operators"])


@router.get("", response_model=list[OperatorResponse])
def list_operators(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[OperatorResponse]:
    return operator_service.get_operators(db, skip=skip, limit=limit)


@router.get("/{operator_id}", response_model=OperatorResponse)
def get_operator(operator_id: int, db: Session = Depends(get_db)) -> OperatorResponse:
    operator = operator_service.get_operator_by_id(db, operator_id)
    if operator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operator with id {operator_id} not found",
        )
    return operator


@router.post("", response_model=OperatorResponse, status_code=status.HTTP_201_CREATED)
def create_operator(
    operator_in: OperatorCreate,
    db: Session = Depends(get_db),
) -> OperatorResponse:
    return operator_service.create_operator(db, operator_in)


@router.put("/{operator_id}", response_model=OperatorResponse)
def update_operator(
    operator_id: int,
    operator_in: OperatorUpdate,
    db: Session = Depends(get_db),
) -> OperatorResponse:
    operator = operator_service.update_operator(db, operator_id, operator_in)
    if operator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operator with id {operator_id} not found",
        )
    return operator


@router.delete("/{operator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_operator(operator_id: int, db: Session = Depends(get_db)) -> None:
    deleted = operator_service.delete_operator(db, operator_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operator with id {operator_id} not found",
        )
