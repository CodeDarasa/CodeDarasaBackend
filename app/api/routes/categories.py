"""Categories API Routes"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.db.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.db.models.course import Course

router = APIRouter()


@router.post("/", response_model=CategoryOut)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    """Create a new category.

This endpoint creates a new category with the provided name. It checks for duplicate category names
and raises an HTTP 400 error if a category with the same name already exists.

Args:
    category (CategoryCreate): The category data to create.
    db (Session): The database session dependency.
    _ (Any): The current authenticated user dependency.

Returns:
    CategoryOut: The newly created category.

Raises:
    HTTPException: If a category with the same name already exists (status code 400)."""
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists.")
    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """List all categories."""

    return db.query(Category).all()


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a category by ID."""

    category = db\
        .query(Category)\
        .options(joinedload(Category.courses))\
        .filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    """Update a category's name/description, and add/remove courses."""
    # Check if the category exists
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Update fields
    if category.name is not None:
        # Check for duplicate name (excluding this category)
        existing = (
            db.query(Category)
            .filter(Category.name == category.name, Category.id != category_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists.")
        db_category.name = category.name

    if category.description is not None:
        db_category.description = category.description

    # Add courses to this category
    if category.add_course_ids:
        courses = db.query(Course).filter(Course.id.in_(category.add_course_ids)).all()
        found_ids = {c.id for c in courses}
        missing = set(category.add_course_ids) - found_ids
        if missing:
            raise HTTPException(status_code=404, detail=f"Courses not found: {sorted(missing)}")
        for c in courses:
            c.category_id = db_category.id

    # Remove courses from this category (sets category_id to None)
    if category.remove_course_ids:
        courses = (
            db.query(Course)
            .filter(Course.id.in_(category.remove_course_ids), Course.category_id == db_category.id)
            .all()
        )
        for c in courses:
            c.category_id = None  # requires nullable=True on Course.category_id

    db.commit()
    db.refresh(db_category)
    # Return with courses included
    return (
        db.query(Category)
        .options(joinedload(Category.courses))
        .filter(Category.id == category_id)
        .first()
    )


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)  # <-- Require authentication
):
    """Delete a category by ID."""

    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"detail": "Category deleted"}
