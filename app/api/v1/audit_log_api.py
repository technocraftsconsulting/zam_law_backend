from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth_dependencies import get_current_user
from app.api.dependencies.dependencies import get_audit_log_service, get_admin_service
from app.api.v1.chat_session_api import get_chat_session_service
from app.models.audit_log import AuditLogRead, AuditLogCreate
from app.services.audit_log_service import AuditLogService

router = APIRouter()


@router.get("", response_model=List[AuditLogRead])
def get_audit_logs(
        audit_log_service: AuditLogService = Depends(get_audit_log_service),
        current_user=Depends(get_current_user)
):
    return audit_log_service.get_audit_logs()


@router.get("/{audit_log_id}", response_model=AuditLogRead)
def get_audit_log(
        audit_log_id: int,
        audit_log_service: AuditLogService = Depends(get_audit_log_service),
        current_user=Depends(get_current_user)
):
    return audit_log_service.get_audit_log(audit_log_id)


@router.delete("/{audit_log_id}")
def delete_audit_log(
        audit_log_id: int,
        audit_log_service: AuditLogService = Depends(get_audit_log_service),
        current_user=Depends(get_current_user)
):
    success = audit_log_service.delete_audit_log(audit_log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Audit Log not found")
    return {"success": True}


@router.post("", response_model=AuditLogRead)
def create_audit_log(
        audit_log: AuditLogCreate,
        chat_session_service=Depends(get_chat_session_service),
        admin_service=Depends(get_admin_service),
        audit_log_service: AuditLogService = Depends(get_audit_log_service),
        current_user=Depends(get_current_user)
):
    return audit_log_service.create_audit_log(
        event_type=audit_log.event_type,
        current_user=current_user.id,
        entity_id=audit_log.entity_id,
        payload=audit_log.payload,
        admin_service=admin_service,
        chat_session=chat_session_service
    )
