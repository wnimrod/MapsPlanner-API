from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    profile_picture: Optional[str]
    is_active: bool
    is_administrator: bool
