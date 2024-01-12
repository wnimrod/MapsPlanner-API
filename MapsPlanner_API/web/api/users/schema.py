from datetime import datetime, date
from typing import Optional, Literal

from pydantic import BaseModel


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    profile_picture: Optional[str]
    is_active: bool
    is_administrator: bool


class UserDetails(User):
    register_date: datetime
    birth_date: Optional[date]
    gender: Optional[Literal["M", "F"]]
    fullname: str
    total_trips: int
    total_markers: int


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    profile_picture: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[Literal["M", "F"]] = None
