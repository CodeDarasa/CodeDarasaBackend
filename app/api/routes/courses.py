from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.course import CourseCreate, CourseOut
from app.crud.course import create_course, get_courses
from app.db.session import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CourseOut)
def create_new_course(course: CourseCreate, db: Session = Depends(get_db)):
    # Check for duplicate by title and youtube_url
    existing = db.query(get_courses.__globals__['Course']).filter_by(
        title=course.title,
        youtube_url=course.youtube_url
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Course with this title and YouTube URL already exists."
        )
    return create_course(db, course)

@router.get("/", response_model=List[CourseOut])
def list_courses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_courses(db, skip=skip, limit=limit)

@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(get_courses.__globals__['Course']).filter_by(id=course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
