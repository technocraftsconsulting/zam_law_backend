from typing import List

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from app.db.db_dependency import get_db
from app.models.chat_session import ChatSessionRead, ChatSessionCreate
from app.services.chat_session_service import ChatSessionService
from app.utils.hashing_util import hash_ip
from app.utils.ip_util import get_client_ip

router = APIRouter()


def get_chat_session_service(db: Session = Depends(get_db)) -> "ChatSessionService":
    return ChatSessionService(session=db)


@router.get("", response_model=List[ChatSessionRead])
def get_chat_sessions(service: ChatSessionService = Depends(get_chat_session_service)):
    return service.list_chat_sessions()


@router.get("/messages", response_model=List[ChatSessionRead])
def get_chat_sessions_with_messages(service: ChatSessionService = Depends(get_chat_session_service)):
    return service.list_sessions_with_messages()


@router.post("", response_model=ChatSessionRead)
def create_chat_session(request: Request, chat_session: ChatSessionCreate,
                        service: ChatSessionService = Depends(get_chat_session_service)):
    ip = get_client_ip(request)
    ip_hash = hash_ip(ip)
    return service.create_chat_session(chat_session.jurisdiction_hint, ip_hash)


@router.delete("/{chat_session_id}")
def delete_chat_session(chat_session_id: int, service: ChatSessionService = Depends(get_chat_session_service)):
    success = service.delete_chat_session(chat_session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"success": True}
