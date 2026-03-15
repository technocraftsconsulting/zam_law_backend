from fastapi import APIRouter, Depends

from app.api.dependencies.dependencies import get_auth_service
from app.api.v1.audit_log_api import get_audit_log_service
from app.models.authentication import TokenResponse, LoginRequest
from app.services.audit_log_service import AuditLogService
from app.services.authentication_service import AuthenticationService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
        login_request: LoginRequest,
        service: AuthenticationService = Depends(get_auth_service),
        audit_log_service: AuditLogService = Depends(get_audit_log_service)
):
    token = service.authenticate(login_request.email, login_request.password, audit_log_service=audit_log_service)
    return TokenResponse(access_token=token)
