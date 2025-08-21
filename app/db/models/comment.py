"""Comment model for the application."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Comment(Base):
    """Represents a comment in the application."""
    __tablename__ = "comments"

    def get_id(self):
        """Returns the ID of the comment."""
        return self.id

    def to_dict(self):
        """Converts the comment to a dictionary representation."""
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id,
            "course_id": self.course_id
        }

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User")
    course = relationship("Course")
