"""Schemas for Category."""
from typing import List, Optional
from pydantic import BaseModel

from app.schemas.course import CourseBrief


class CategoryBase(BaseModel):
    """Base schema for Category."""
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a new Category."""


class CategoryUpdate(BaseModel):
    """Schema for updating an existing Category."""
    name: Optional[str] = None
    description: Optional[str] = None
    add_course_ids: Optional[List[int]] = None
    remove_course_ids: Optional[List[int]] = None


class CategoryOut(CategoryBase):
    """Schema for outputting Category data."""
    id: int
    name: str
    description: Optional[str] = None
    courses: List[CourseBrief] = []

    model_config = {
        "from_attributes": True
    }
