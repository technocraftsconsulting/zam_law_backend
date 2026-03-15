from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.dependencies import get_message_service, get_audit_log_service
from app.db import ChatSession
from app.models.message import MessageRead, MessageCreate
from app.services.audit_log_service import AuditLogService
from app.services.message_service import MessageService
from app.utils.session_util import get_current_chat_session

router = APIRouter()


@router.post("", response_model=MessageRead)
def create_message(message: MessageCreate, current_session: ChatSession = Depends(get_current_chat_session),
                   service: MessageService = Depends(get_message_service),
                   audit_log_service: AuditLogService = Depends(get_audit_log_service)):
    return service.create_message(chat_session=current_session, content=message.content,
                                  audit_log_service=audit_log_service)


@router.delete("/{message_id}")
def delete_message(
        message_id: int,
        current_session: ChatSession = Depends(get_current_chat_session),
        service: MessageService = Depends(get_message_service)
):
    success = service.delete_message(message_id=message_id, session=current_session)

    if not success:
        raise HTTPException(status_code=404, detail="Message not found")

    return {"success": True}


@router.get("/chat", response_model=List[MessageRead])
def get_messages_by_chat(current_session: ChatSession = Depends(get_current_chat_session),
                         service: MessageService = Depends(get_message_service)):
    return service.list_messages_by_chat_session(session=current_session)
