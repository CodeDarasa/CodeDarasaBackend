"""Category model for the course management system."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Category(Base):
    """Category model representing a course category."""
    __tablename__ = "categories"

    def get_id(self):
        """Returns the ID of the category."""
        return self.id

    def to_dict(self):
        """Converts the category to a dictionary representation with all details."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "courses": [course.id for course in self.courses] if self.courses else []
        }

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    courses = relationship("Course", back_populates="category")
