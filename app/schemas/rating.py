"""Schemas for rating-related operations."""
from pydantic import BaseModel, conint


class RatingCreate(BaseModel):
    """Schema for creating a new rating."""
    value: conint(ge=1, le=5)


class RatingOut(BaseModel):
    """Schema for outputting rating data."""
    id: int
    value: int
    user_id: int
    course_id: int

    class Config:
        """Configuration for RatingOut schema."""
        from_attributes = True
