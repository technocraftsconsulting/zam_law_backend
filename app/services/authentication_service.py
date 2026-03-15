from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.schema import UserRole, EventType
from app.services.admin_service import AdminService
from app.services.audit_log_service import AuditLogService
from app.utils.hashing_util import verify_password


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.session_expiry_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.session_secret_key, algorithm=settings.algorithm)


class AuthenticationService:
    def __init__(self, session: Session):
        self._db = session
        self.admin_service = AdminService(session=session)

    def authenticate(self, email: str, password: str, audit_log_service: AuditLogService) -> str:
        user = self.admin_service.get_admin_by_email(email)

        if not user:
            audit_log_service.create_audit_log(
                event_type=EventType.ADMIN_LOGIN_FAILED.name,
                current_user=user.id,
                admin_service=self.admin_service
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(password=password, password_hash=user.password_hash):
            audit_log_service.create_audit_log(
                event_type=EventType.ADMIN_LOGIN_FAILED.name,
                current_user=user.id,
                admin_service=self.admin_service
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if user.role == UserRole.ADMIN:
            audit_log_service.create_audit_log(
                event_type=EventType.ADMIN_LOGIN.name,
                current_user=user.id,
                admin_service=self.admin_service
            )
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email
            }
        )
        return access_token
