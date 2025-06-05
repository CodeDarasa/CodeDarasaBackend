from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.course import CourseCreate, CourseInDB
from app.crud.course import create_course, get_courses
from app.api.deps import get_db
from typing import List

router = APIRouter()

@router.post("/courses/", response_model=CourseInDB)
def create(course: CourseCreate, db: Session = Depends(get_db)):
    return create_course(db, course)

@router.get("/courses/", response_model=List[CourseInDB])
def list_courses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_courses(db, skip=skip, limit=limit)
