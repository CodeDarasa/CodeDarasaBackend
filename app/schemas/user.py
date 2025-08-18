from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }


class UserUpdate(UserBase):
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
