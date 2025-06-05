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
    return create_course(db, course)

@router.get("/", response_model=List[CourseOut])
def list_courses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_courses(db, skip=skip, limit=limit)
