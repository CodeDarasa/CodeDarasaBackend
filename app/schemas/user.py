"""User schemas for Pydantic validation and serialization."""
from typing import Optional
from enum import Enum
from pydantic import BaseModel


class UserRole(str, Enum):
    """Enumeration for user roles."""
    ADMIN = "ADMIN"
    USER = "USER"


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
    role: UserRole

    model_config = {
        "from_attributes": True
    }


class UserUpdate(UserBase):
    """Schema for updating an existing User."""
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
