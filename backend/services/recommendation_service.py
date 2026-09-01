from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.recommendation import Recommendation
from schemas.recommendation import RecommendationCreate, RecommendationUpdate


def create_recommendation(db: Session, recommendation_in: RecommendationCreate) -> Recommendation:
    recommendation_data = recommendation_in.model_dump()
    if recommendation_data.get("recommendation_time") is None:
        recommendation_data["recommendation_time"] = datetime.now(timezone.utc)

    recommendation = Recommendation(**recommendation_data)
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation


def get_recommendations(db: Session, skip: int = 0, limit: int = 100) -> list[Recommendation]:
    stmt = select(Recommendation).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_recommendation_by_id(db: Session, recommendation_id: int) -> Recommendation | None:
    return db.get(Recommendation, recommendation_id)


def update_recommendation(
    db: Session,
    recommendation_id: int,
    recommendation_in: RecommendationUpdate,
) -> Recommendation | None:
    recommendation = db.get(Recommendation, recommendation_id)
    if recommendation is None:
        return None

    update_data = recommendation_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recommendation, field, value)

    db.commit()
    db.refresh(recommendation)
    return recommendation


def delete_recommendation(db: Session, recommendation_id: int) -> bool:
    recommendation = db.get(Recommendation, recommendation_id)
    if recommendation is None:
        return False

    db.delete(recommendation)
    db.commit()
    return True
