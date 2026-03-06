from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.message import MessageRead


class ChatSessionCreate(BaseModel):
    jurisdiction_hint: str


class ChatSessionRead(BaseModel):
    id: int
    session_token: str
    jurisdiction_hint: str
    ip_hash: str
    created_at: datetime
    expires_at: datetime
    messages: Optional[List[MessageRead]]
