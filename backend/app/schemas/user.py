from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.enums import UserRole


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.user)


class UserCreate(UserBase):
    password: str = Field(min_length=4)


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
