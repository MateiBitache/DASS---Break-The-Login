from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.exceptions import AuthException
from app.models import AuditLog, User, UserRole
from app.security import decode_token

router = APIRouter(prefix="/api/audit", tags=["audit"])

def _get_manager_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthException("Invalid credentials")
    
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload or "userId" not in payload:
        raise AuthException("Invalid credentials")
        
    user = db.query(User).filter(User.id == payload["userId"]).first()

    if not user or user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise AuthException("Access denied: Requires MANAGER clearance")
        
    return user

@router.get("")
def get_audit_logs(user: User = Depends(_get_manager_user), db: Session = Depends(get_db)):

    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return [
        {
            "id": log.id,
            "userEmail": log.user.email if log.user else "System",
            "action": log.action,
            "resource": log.resource,
            "details": log.details,
            "ipAddress": log.ip_address,
            "timestamp": log.timestamp.isoformat(),
            "success": log.success
        } for log in logs
    ]