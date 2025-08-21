"""Rating model for storing user ratings of courses."""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Rating(Base):
    """Represents a rating given by a user to a course."""
    __tablename__ = "ratings"

    def get_id(self):
        """Returns the ID of the rating."""
        return self.id

    def to_dict(self):
        """Converts the rating to a dictionary representation."""
        return {
            "id": self.id,
            "value": self.value,
            "user_id": self.user_id,
            "course_id": self.course_id
        }

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, nullable=False)  # 1-5
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User")
    course = relationship("Course")
    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='_user_course_uc'),)
