from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AdminCreate(BaseModel):
    email: str
    password: str
    full_name: str


class AdminUpdate(BaseModel):
    email: str
    password: str
    full_name: str


class AdminRead(BaseModel):
    id: int
    full_name: str
    is_active: bool
    # last_login: datetime | None
    created_at: datetime
