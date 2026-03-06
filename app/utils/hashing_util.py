import hashlib
import hmac

from app.core.config import settings


def hash_ip(ip: str) -> str:
    return hmac.new(
        settings.ip_hash_secret_key.encode(),
        ip.encode(),
        hashlib.sha256
    ).hexdigest()
