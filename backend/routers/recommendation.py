from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.recommendation import RecommendationCreate, RecommendationResponse, RecommendationUpdate
from services import recommendation_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationResponse])
def list_recommendations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[RecommendationResponse]:
    return recommendation_service.get_recommendations(db, skip=skip, limit=limit)


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    recommendation = recommendation_service.get_recommendation_by_id(db, recommendation_id)
    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation with id {recommendation_id} not found",
        )
    return recommendation


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
def create_recommendation(
    recommendation_in: RecommendationCreate,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    return recommendation_service.create_recommendation(db, recommendation_in)


@router.put("/{recommendation_id}", response_model=RecommendationResponse)
def update_recommendation(
    recommendation_id: int,
    recommendation_in: RecommendationUpdate,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    recommendation = recommendation_service.update_recommendation(
        db,
        recommendation_id,
        recommendation_in,
    )
    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation with id {recommendation_id} not found",
        )
    return recommendation


@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recommendation(recommendation_id: int, db: Session = Depends(get_db)) -> None:
    deleted = recommendation_service.delete_recommendation(db, recommendation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation with id {recommendation_id} not found",
        )
