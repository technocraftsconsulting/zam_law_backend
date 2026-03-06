from datetime import datetime
from typing import List

from pydantic import BaseModel


class AdminCreate(BaseModel):
    email: str
    password_hash: str
    full_name: str
    is_active: bool


class AdminRead(BaseModel):
    id: int
    full_name: str
    is_active: bool
    last_login: datetime
    created_at: datetime
    audit_logs: List[AuditLogRead]

