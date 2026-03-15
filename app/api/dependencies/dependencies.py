from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.db_dependency import get_db
from app.services.admin_service import AdminService
from app.services.audit_log_service import AuditLogService
from app.services.authentication_service import AuthenticationService
from app.services.chat_session_service import ChatSessionService
from app.services.current_user_service import CurrentUserService
from app.services.document_service import DocumentService
from app.services.message_service import MessageService


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(session=db)


def get_chat_session_service(db: Session = Depends(get_db)) -> ChatSessionService:
    return ChatSessionService(session=db)


def get_audit_log_service(db: Session = Depends(get_db)) -> AuditLogService:
    return AuditLogService(session=db)


def get_auth_service(db: Session = Depends(get_db)) -> AuthenticationService:
    return AuthenticationService(session=db)


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)


def get_message_service(db: Session = Depends(get_db)) -> "MessageService":
    return MessageService(session=db)


def get_current_user_service(db: Session = Depends(get_db)) -> CurrentUserService:
    return CurrentUserService(db)
