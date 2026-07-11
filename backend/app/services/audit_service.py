from typing import Any

from sqlmodel import Session

from app.models import AuditLog


def log_change(
    session: Session,
    table_name: str,
    record_id: int | None,
    action: str,
    changes: dict[str, Any] | None,
    user_id: str | None = None,
    organization_id: int | None = None,
) -> AuditLog:
    log = AuditLog(
        table_name=table_name,
        record_id=record_id,
        action=action,
        changes=changes or {},
        user_id=user_id,
        organization_id=organization_id,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log
