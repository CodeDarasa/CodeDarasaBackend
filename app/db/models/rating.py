from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.models.course import Base

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, nullable=False)  # 1-5
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    user = relationship("User")
    course = relationship("Course")
    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='_user_course_uc'),)
    