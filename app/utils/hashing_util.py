import hashlib
import hmac

from app.config.passlib_config import pwd_context
from app.core.config import settings


def hash_ip(ip: str) -> str:
    return hmac.new(
        settings.ip_hash_secret_key.encode(),
        ip.encode(),
        hashlib.sha256
    ).hexdigest()


def create_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


