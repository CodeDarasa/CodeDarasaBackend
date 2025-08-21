"""User schemas for Pydantic validation and serialization."""
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    """Base schema for User."""
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new User."""
    password: str


class UserOut(UserBase):
    """Schema for outputting User data."""
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }


class UserUpdate(UserBase):
    """Schema for updating an existing User."""
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
