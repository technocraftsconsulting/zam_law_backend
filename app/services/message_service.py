from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.db import Message, ChatSession
from app.db.schema import MessageRole


class MessageService:
    def __init__(self, session: Session):
        self._db = session

    def validate_session_token(self, session_token: str) -> str:
        session = self._db.execute(
            select(ChatSession)
            .where(ChatSession.session_token == session_token)
            .where(ChatSession.expires_at > datetime.now(timezone.utc))
        )
        session = session.scalar_one_or_none()
        return session

    def get_message(self, message_id: int) -> Message | None:
        result = self._db.scalars(select(Message).where(Message.id == message_id))
        return result.first()

    def list_messages_by_chat_session(self, session: ChatSession) -> list[Message]:
        result = self._db.scalars(
            select(Message).where(Message.session_id == session.id)
        )
        return list(result)


    def create_message(self, chat_session: ChatSession, content: str) -> Message:
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
