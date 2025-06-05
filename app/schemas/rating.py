from pydantic import BaseModel, conint

class RatingCreate(BaseModel):
    value: conint(ge=1, le=5)

class RatingOut(BaseModel):
    id: int
    value: int
    user_id: int
    course_id: int

    class Config:
        orm_mode = True
