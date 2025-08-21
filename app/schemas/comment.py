"""Schemas for comment-related operations."""
from datetime import datetime
from pydantic import BaseModel


class CommentCreate(BaseModel):
    """Schema for creating a new comment."""
    content: str


class CommentOut(BaseModel):
    """Schema for outputting comment data."""
    id: int
    content: str
    created_at: datetime
    user_id: int
    course_id: int

    class Config:
        """Configuration for CommentOut schema."""
        from_attributes = True
