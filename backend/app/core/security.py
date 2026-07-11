import base64
import hashlib
import secrets
from typing import Any

from cryptography.fernet import Fernet
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fernet key must be 32 bytes url-safe base64.
# If ENCRYPTION_KEY is not provided, derive one from SECRET_KEY (NOT recommended for production,
# but avoids crashes in demo/testing). In production, set a real ENCRYPTION_KEY.
_fernet: Fernet | None = None


def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = settings.encryption_key
        if not key:
            # Derive a 32-byte base64 key from SECRET_KEY; stable across restarts.
            derived = base64.urlsafe_b64encode(
                hashlib.sha256(settings.secret_key.encode()).digest()
            )
            key = derived.decode()
        try:
            _fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as exc:
            # Fallback: generate a random key. Note: existing encrypted data will be lost.
            _fernet = Fernet(Fernet.generate_key())
    return _fernet


def encrypt(value: str) -> str:
    return get_fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return get_fernet().decrypt(value.encode()).decode()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_secret(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


# Expose fernet for EncryptedString TypeDecorator
fernet = get_fernet()
