"""User model for the application."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """Represents a user in the application."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # Add more profile fields as needed, e.g.:
    full_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    courses = relationship("Course", back_populates="creator")
