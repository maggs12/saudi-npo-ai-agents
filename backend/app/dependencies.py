import hmac

from fastapi import HTTPException, Request

from app.core.config import settings
from app.database import SessionLocal, get_session


def get_db():
    with SessionLocal() as session:
        yield session


def api_key_header(request: Request) -> None:
    """Require X-API-Key when API_KEY is configured."""
    if not settings.api_key:
        return
    provided = request.headers.get("X-API-Key") or ""
    if not hmac.compare_digest(provided, settings.api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
