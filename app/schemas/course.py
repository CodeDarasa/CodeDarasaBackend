from pydantic import BaseModel

class CourseBase(BaseModel):
    title: str
    description: str
    youtube_url: str

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int

    class Config:
        orm_mode = True
