from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Admin
from app.db.schema import UserRole
from app.utils.hashing_util import create_password_hash


class AdminService:
    def __init__(self, session: Session):
        self._db = session

    def create_admin(self, email: str, password: str, full_name: str) -> Admin | None:
        admin = Admin(
            email=email,
            password_hash=create_password_hash(password=password),
            full_name=full_name,
            role=UserRole.ADMIN.name,
            is_active=True
        )
        self._db.add(admin)
        self._db.commit()
        self._db.refresh(admin)
        return admin

    def get_admin(self, admin_id: int) -> Admin | None:
        result = self._db.scalars(select(Admin).where(Admin.id == admin_id))
        return result.first()

    def delete_admin(self, admin_id: int) -> bool:
        admin = self.get_admin(admin_id)
        if not admin:
            return False
        self._db.delete(admin)
        self._db.commit()
        return True

    def get_admins(self) -> list[Admin]:
        result = self._db.scalars(select(Admin))
        return list(result)

    def update_message(self, admin_id: int, email: str, full_name: str) -> Admin | None:
        admin = self.get_admin(admin_id)
        if not admin:
            return None
        admin.email = email
        admin.full_name = full_name
        self._db.commit()
        self._db.refresh(admin)
        return admin

    def get_admin_by_email(self, email: str) -> Admin | None:
        result = self._db.scalars(select(Admin).where(Admin.email == email))
        return result.first()
