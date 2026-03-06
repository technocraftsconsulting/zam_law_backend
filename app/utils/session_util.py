import secrets
from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import ChatSession
from app.db.db_dependency import get_db

security = HTTPBearer()


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def get_expiry():
    session_expiry_minutes = settings.session_expiry_minutes
    return datetime.now(timezone.utc) + timedelta(minutes=session_expiry_minutes)


def get_current_chat_session(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
) -> ChatSession:
    token = credentials.credentials

    chat_session = db.scalar(
        select(ChatSession)
        .where(ChatSession.session_token == token)
        .where(ChatSession.expires_at > datetime.now(timezone.utc))
    )

    if not chat_session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return chat_session
