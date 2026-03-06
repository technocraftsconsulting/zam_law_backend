from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: int
    role: str
    content: str
    turn_index: int
    created_at: datetime
