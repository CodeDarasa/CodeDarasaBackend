"""Ratings API Routes"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.course import Course
from app.db.models.rating import Rating
from app.schemas.rating import RatingCreate, RatingOut

router = APIRouter()


@router.post("/courses/{course_id}/ratings/", response_model=RatingOut)
def rate_course(course_id: int, rating: RatingCreate, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    """Rate a course."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    existing = db\
        .query(Rating)\
        .filter(Rating.user_id == current_user.id, Rating.course_id == course_id)\
        .first()
    if existing:
        existing.value = rating.value
        db.commit()
        db.refresh(existing)
        return existing
    db_rating = Rating(value=rating.value, user_id=current_user.id, course_id=course_id)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


@router.get("/courses/{course_id}/ratings/", response_model=List[RatingOut])
def course_ratings(course_id: int, db: Session = Depends(get_db)):
    """List all ratings for a course."""
    return db.query(Rating).filter(Rating.course_id == course_id).all()


@router.delete("/courses/{course_id}/ratings/{rating_id}", response_model=dict)
def delete_rating(
    course_id: int,
    rating_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Delete a rating for a course."""
    db_rating = db\
        .query(Rating)\
        .filter(Rating.course_id == course_id)\
        .filter(Rating.id == rating_id)\
        .first()
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if db_rating.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this rating")
    db.delete(db_rating)
    db.commit()
    return {"detail": "Rating deleted successfully"}
