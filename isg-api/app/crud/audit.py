from sqlalchemy.orm import Session
from typing import Optional, Any
from app.models.role import AuditLog


def log_action(db: Session, user_id: int, action: str, target: Optional[str] = None, metadata: Optional[Any] = None) -> AuditLog:
    entry = AuditLog(user_id=user_id, action=action, target=target, event_metadata=metadata)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_audit_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
