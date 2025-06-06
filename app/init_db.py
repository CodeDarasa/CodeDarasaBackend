from app.db.models.course import Base
from app.db.models import user, course, category, comment, rating
from app.db.session import engine

def init():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init()
