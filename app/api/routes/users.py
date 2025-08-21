"""User management routes for the FastAPI application."""
from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.rating import Rating
from app.db.models.user import User
from app.schemas.rating import RatingOut
from app.schemas.user import UserCreate
from app.schemas.user import UserOut, UserUpdate

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(db: Session, username: str):
    """Retrieve a user by username."""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate):
    """Create a new user in the database."""
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return current_user


@router.put("/me", response_model=UserOut)
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the current user's profile."""
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    if user_update.bio is not None:
        db_user.bio = user_update.bio
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me/ratings/", response_model=list[RatingOut])
def user_ratings(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """List all ratings made by the current user."""
    return db.query(Rating).filter(Rating.user_id == current_user.id).all()


def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)
