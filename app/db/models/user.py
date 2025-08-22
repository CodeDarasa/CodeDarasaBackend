"""User model for the application."""
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserRole(str, PyEnum):
    """Enumeration for user roles."""
    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    """Represents a user in the application."""
    __tablename__ = "users"

    def get_id(self):
        """Returns the ID of the user."""
        return self.id

    def to_dict(self):
        """Converts the user to a dictionary representation."""
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "bio": self.bio,
            "role": self.role.value if hasattr(self.role, "value") else self.role,
        }

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    role = Column(
        SQLEnum(UserRole, name="user_role"),
        nullable=False,
        server_default=UserRole.USER.value,
        index=True,
        default=UserRole.USER
    )
    courses = relationship("Course", back_populates="creator")
