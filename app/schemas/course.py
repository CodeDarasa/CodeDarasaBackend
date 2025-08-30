"""Schemas for Course"""
import datetime
from typing import List, Optional

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


class CourseBrief(BaseModel):
    """Brief schema for Course, used in lists or summaries."""
    id: int
    title: str

    class Config:
        """Configuration for CourseBrief schema."""
        orm_mode = True


class CourseOut(CourseBase):
    """Schema for outputting Course data."""
    id: int
    category_id: Optional[int] = None
    creator: UserOut
    created_at: datetime.datetime

    model_config = {
        "from_attributes": True
    }


class CourseListOut(BaseModel):
    """Schema for outputting a list of Courses."""
    items: List[CourseOut]
    total: int

    class Config:
        """Configuration for CourseListOut schema."""
        from_attributes = True
