"""This script initializes the database by creating all tables defined in the models."""
from app.db.models.course import Base
from app.db.session import engine


def init():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init()
