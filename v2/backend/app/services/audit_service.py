from sqlalchemy.orm import Session

from app.models import AuditLog, User


def log_event(
    db: Session,
    user: User,
    action: str,
    resource: str,
    resource_id: str,
    details: str,
    ip_address: str,
    success: bool,
):
    audit_log = AuditLog(
        user=user,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        success=success,
    )
    db.add(audit_log)
    db.commit()
