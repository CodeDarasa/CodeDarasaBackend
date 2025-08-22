"""Base class for SQLAlchemy models."""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models so they are registered with Base.metadata
# pylint: disable=unused-import, wrong-import-position
from app.db.models import category  # noqa: F401
from app.db.models import course    # noqa: F401
from app.db.models import comment   # noqa: F401
from app.db.models import rating    # noqa: F401
from app.db.models import user      # noqa: F401
