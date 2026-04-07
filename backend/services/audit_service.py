from sqlalchemy.orm import Session

from backend.db.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    actor_user_id: int | None,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    detail_json: dict | None = None,
) -> AuditLog:
    audit = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail_json=detail_json,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
