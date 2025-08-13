from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.category import Category
from app.schemas.category import CategoryCreate, CategoryOut
from app.api.deps import get_current_user, get_db
from typing import List

router = APIRouter()

@router.post("/", response_model=CategoryOut)
def create_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
    ):
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists.")
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int, 
    category: CategoryCreate, 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    # Check for duplicate name (excluding this category)
    existing = db.query(Category).filter(Category.name == category.name, Category.id != category_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists.")
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)  # <-- Require authentication
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"detail": "Category deleted"}
