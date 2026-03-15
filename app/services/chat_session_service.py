from datetime import timedelta, datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import ChatSession
from app.db.schema import EventType
from app.services.audit_log_service import AuditLogService
from app.utils.session_util import generate_session_token


class ChatSessionService:
    def __init__(self, session: Session):
        self._db = session

    def list_chat_sessions(self) -> list[ChatSession]:
        result = self._db.scalars(select(ChatSession))
        return list(result)

    def get_chat_session(self, chat_id: int) -> ChatSession | None:
        result = self._db.scalars(select(ChatSession).where(ChatSession.id == chat_id))
        return result.first()

    def create_chat_session(
            self,
            jurisdiction_hint: str,
            ip_hash: str,
            audit_log_service: AuditLogService,
            expires_at: Optional[datetime] = None,
    ) -> ChatSession:
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        token = generate_session_token()

        chat_session = ChatSession(
            session_token=token,
            jurisdiction_hint=jurisdiction_hint,
            ip_hash=ip_hash,
            expires_at=expires_at,
        )

        self._db.add(chat_session)
        self._db.commit()
        self._db.refresh(chat_session)

        audit_log_service.create_audit_log(
            event_type=EventType.SESSION_CREATED.name,
            chat_session=chat_session
        )
        return chat_session

    def delete_chat_session(self, chat_id: int) -> bool:
        chat_session = self.get_chat_session(chat_id)
        if not chat_session:
            return False
        self._db.delete(chat_session)
        self._db.commit()
        return True

    def list_sessions_with_messages(self) -> list[ChatSession]:
        result = self._db.scalars(
            select(ChatSession).options(selectinload(ChatSession.messages))
        )
        return list(result)
