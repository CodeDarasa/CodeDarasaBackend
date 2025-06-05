from typing import Optional
from app.schemas.category import CategoryOut
from app.schemas.user import UserOut
from pydantic import BaseModel

class CourseBase(BaseModel):
    title: str
    description: str
    youtube_url: str
    category_id: Optional[int] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int
    category_id: Optional[int] = None
    creator: UserOut

    model_config = {
        "from_attributes": True
    }
