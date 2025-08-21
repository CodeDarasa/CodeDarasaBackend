"""User model for the application."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


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
            "bio": self.bio
        }

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # Add more profile fields as needed, e.g.:
    full_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    courses = relationship("Course", back_populates="creator")
