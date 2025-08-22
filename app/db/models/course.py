"""Course model for the database."""
from sqlalchemy import Column, DateTime, func, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Course(Base):
    """Represents a course in the application."""
    __tablename__ = "courses"

    def get_id(self):
        """Returns the ID of the course."""
        return self.id

    def to_dict(self):
        """Converts the course to a dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "youtube_url": self.youtube_url
        }

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    youtube_url = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    category = relationship("Category", back_populates="courses")
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="courses")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
