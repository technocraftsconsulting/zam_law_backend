from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from app.core.config import settings
from app.db import Admin
from app.db.db_dependency import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class CurrentUserService:
    def __init__(self, session: Session):
        self._db = session

    def get_current_user(self, token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

        try:
            payload = jwt.decode(
                token,
                settings.session_secret_key,
                algorithms=[settings.algorithm]
            )
            user_id = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = self._db.get(Admin, int(user_id))
        if user is None:
            raise credentials_exception

        return user