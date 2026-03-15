from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db import Message, ChatSession
from app.db.schema import MessageRole, EventType
from app.services.audit_log_service import AuditLogService


class MessageService:
    def __init__(self, session: Session):
        self._db = session

    def get_message(self, message_id: int) -> Message | None:
        result = self._db.scalars(select(Message).where(Message.id == message_id))
        return result.first()

    def list_messages_by_chat_session(self, session: ChatSession) -> list[Message]:
        result = self._db.scalars(
            select(Message).where(Message.session_id == session.id)
        )
        return list(result)

    def create_message(self, chat_session: ChatSession, content: str, audit_log_service: AuditLogService) -> Message:
        result = self._db.scalar(
            select(func.count(Message.id))
            .where(Message.session_id == chat_session.id)
        )

        turn_index = result + 1

        message = Message(
            session_id=chat_session.id,
            content=content,
            role=MessageRole.USER,
            turn_index=turn_index
        )

        self._db.add(message)
        self._db.commit()
        self._db.refresh(message)

        audit_log_service.create_audit_log(
            event_type=EventType.MESSAGE_SENT.name,
            chat_session=chat_session,
            entity_id=message.id,
            payload=list(str(message))
        )

        return message

    def delete_message(self, message_id: int, session: ChatSession) -> bool:
        message = self._db.scalar(
            select(Message)
            .where(Message.id == message_id)
            .where(Message.session_id == session.id)
        )

        if not message:
            return False

        self._db.delete(message)
        self._db.commit()
        return True

    def update_message(self, message_id: int, content: str, turn_index: int) -> Message | None:
        message = self.get_message(message_id)
        if not message:
            return None
        message.content = content
        message.turn_index = turn_index
        self._db.commit()
        self._db.refresh(message)
        return message
