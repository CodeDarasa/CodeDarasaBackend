from sqlalchemy.orm import Session
from app.db.models.course import Course
from app.schemas.course import CourseCreate

def create_course(db: Session, course: CourseCreate):
    db_course = Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_courses(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Course).offset(skip).limit(limit).all()
