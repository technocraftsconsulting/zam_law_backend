from datetime import datetime
from typing import List

from pydantic import BaseModel


class AuditLogCreate(BaseModel):
    admin_id: int
    session_id: int
    event_type: str
    entity_id: str
    payload: List[str]


class AuditLogRead(BaseModel):
    id: int
    admin_id: int
    session_id: int
    event_type: str
    entity_id: str
    payload: List[str]
    created_at: datetime
