from typing import Optional
from app.schemas.category import CategoryOut
from pydantic import BaseModel

class CourseBase(BaseModel):
    title: str
    description: str
    youtube_url: str
    category_id: Optional[int] = None

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int
    category: Optional[CategoryOut] = None

    model_config = {
        "from_attributes": True
    }
