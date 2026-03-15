from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import ChatSession, AuditLog
from app.services.admin_service import AdminService


class AuditLogService:
    def __init__(self, session: Session):
        self._db = session

    def create_audit_log(
            self,
            event_type: str,
            current_user: Optional[int] = None,
            entity_id: Optional[UUID] = None,
            payload: Optional[List[str]] = None,
            admin_service: Optional[AdminService] = None,
            chat_session: Optional[ChatSession] = None
    ):
        data = {
            "event_type": event_type,
            "entity_id": entity_id,
            "payload": payload
        }

        if admin_service:
            admin = admin_service.get_admin(current_user)
            data["admin_id"] = admin.id

        if chat_session:
            data["session_id"] = chat_session.id

        audit_log = AuditLog(**data)

        self._db.add(audit_log)
        self._db.commit()
        self._db.refresh(audit_log)

        return audit_log

    def get_audit_log(self, audit_log_id: int) -> Optional[AuditLog]:
        result = self._db.scalars(select(AuditLog).where(AuditLog.id == audit_log_id))
        return result.first()

    def get_audit_logs(self) -> List[AuditLog]:
        result = self._db.scalars(select(AuditLog))
        return list(result)

    def get_audit_log_by_event_type(self, event_type: str) -> Optional[List[AuditLog]]:
        result = self._db.scalars(select(AuditLog).where(AuditLog.event_type == event_type))
        return list(result)

    def delete_audit_log(self, audit_log_id: int) -> bool:
        audit_log = self.get_audit_log(audit_log_id)
        if not audit_log:
            return False
        self._db.delete(audit_log)
        self._db.commit()
        return True
