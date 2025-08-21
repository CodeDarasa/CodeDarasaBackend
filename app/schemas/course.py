"""Schemas for Course"""
from typing import Optional

from pydantic import BaseModel

from app.schemas.user import UserOut


class CourseBase(BaseModel):
    """Base schema for Course."""
    title: str
    description: str
    youtube_url: str
    category_id: Optional[int] = None


class CourseCreate(CourseBase):
    """Schema for creating a new Course."""


class CourseUpdate(CourseBase):
    """Schema for updating an existing Course."""


class CourseOut(CourseBase):
    """Schema for outputting Course data."""
    id: int
    category_id: Optional[int] = None
    creator: UserOut

    model_config = {
        "from_attributes": True
    }
