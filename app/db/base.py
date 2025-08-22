"""Base class for SQLAlchemy models."""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models so they are registered with Base.metadata
# pylint: disable=unused-import, wrong-import-position
from app.db.models.category import Category  # noqa: F401
from app.db.models.course import Course      # noqa: F401
from app.db.models.comment import Comment    # noqa: F401
from app.db.models.rating import Rating      # noqa: F401
from app.db.models.user import User          # noqa: F401
