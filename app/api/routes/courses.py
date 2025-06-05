from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_current_user
from app.schemas.course import CourseCreate, CourseOut
from app.db.models.course import Course
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
def create_new_course(
    course: CourseCreate, 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
    ):

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
def list_courses(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search by title"),
):
    query = db.query(Course)
    if search:
        query = query.filter(Course.title.ilike(f"%{search}%"))
    courses = query.offset((page - 1) * page_size).limit(page_size).all()
    return courses

@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(get_courses.__globals__['Course']).filter_by(id=course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{course_id}", response_model=CourseOut)
def update_course(
    course_id: int,
    course_update: CourseCreate = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    course = db.query(get_courses.__globals__['Course']).filter_by(id=course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check for duplicate (excluding current course)
    duplicate = db.query(get_courses.__globals__['Course']).filter(
        get_courses.__globals__['Course'].id != course_id,
        get_courses.__globals__['Course'].title == course_update.title,
        get_courses.__globals__['Course'].youtube_url == course_update.youtube_url
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Another course with this title and YouTube URL already exists."
        )

    course.title = course_update.title
    course.description = course_update.description
    course.youtube_url = course_update.youtube_url

    db.commit()
    db.refresh(course)

    return course

@router.delete("/{course_id}", status_code=200)
def delete_course(
    course_id: int, 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    course = db.query(get_courses.__globals__['Course']).filter_by(id=course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully."}
