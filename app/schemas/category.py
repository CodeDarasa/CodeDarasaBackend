"""Schemas for Category."""
from pydantic import BaseModel


class CategoryBase(BaseModel):
    """Base schema for Category."""
    name: str


class CategoryCreate(CategoryBase):
    """Schema for creating a new Category."""

class CategoryOut(CategoryBase):
    """Schema for outputting Category data."""
    id: int

    model_config = {
        "from_attributes": True
    }
