from typing import Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.violation import Violation, ViolationStatus, ViolationType, ViolationSeverity
from app.models.safety_rule import SafetyRuleType
from app.schemas.violation import ViolationCreate, ViolationUpdate


def get_violation(db: Session, violation_id: int) -> Optional[Violation]:
    """Get violation by ID"""
    return db.query(Violation).filter(Violation.id == violation_id).first()


def get_violations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    factory_area_id: Optional[int] = None,
    violation_type: Optional[ViolationType] = None,
    rule_type: Optional[SafetyRuleType] = None,
    severity: Optional[ViolationSeverity] = None,
    status: Optional[ViolationStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> list[Violation]:
    """Get multiple violations with optional filters"""
    query = db.query(Violation)
    
    if employee_id:
        query = query.filter(Violation.employee_id == employee_id)
    
    if camera_id:
        query = query.filter(Violation.camera_id == camera_id)

    if factory_area_id:
        query = query.filter(Violation.factory_area_id == factory_area_id)
    
    if violation_type:
        query = query.filter(Violation.violation_type == violation_type)

    if rule_type:
        query = query.filter(Violation.rule_type == rule_type)
    
    if severity:
        query = query.filter(Violation.severity == severity)
    
    if status:
        query = query.filter(Violation.status == status)
    
    if start_date:
        query = query.filter(func.date(Violation.created_at) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Violation.created_at) <= end_date)
    
    return (
        query.order_by(
            func.coalesce(Violation.occurred_at, Violation.created_at).desc(),
            Violation.created_at.desc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_violations(
    db: Session,
    employee_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    factory_area_id: Optional[int] = None,
    violation_type: Optional[ViolationType] = None,
    rule_type: Optional[SafetyRuleType] = None,
    severity: Optional[ViolationSeverity] = None,
    status: Optional[ViolationStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> int:
    """Count violations with optional filters"""
    query = db.query(Violation)
    
    if employee_id:
        query = query.filter(Violation.employee_id == employee_id)
    
    if camera_id:
        query = query.filter(Violation.camera_id == camera_id)

    if factory_area_id:
        query = query.filter(Violation.factory_area_id == factory_area_id)
    
    if violation_type:
        query = query.filter(Violation.violation_type == violation_type)

    if rule_type:
        query = query.filter(Violation.rule_type == rule_type)
    
    if severity:
        query = query.filter(Violation.severity == severity)
    
    if status:
        query = query.filter(Violation.status == status)
    
    if start_date:
        query = query.filter(func.date(Violation.created_at) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Violation.created_at) <= end_date)
    
    return query.count()


def create_violation(db: Session, violation: ViolationCreate) -> Violation:
    """Create new violation"""
    occurred_at = violation.occurred_at or datetime.utcnow()
    db_violation = Violation(
        employee_id=violation.employee_id,
        camera_id=violation.camera_id,
        factory_area_id=violation.factory_area_id,
        violation_type=violation.violation_type,
        rule_type=violation.rule_type,
        severity=violation.severity,
        status=violation.status,
        description=violation.description,
        image_url=violation.image_url,
        video_url=violation.video_url,
        confidence_score=violation.confidence_score,
        bbox_coordinates=violation.bbox_coordinates,
        occurred_at=occurred_at,
        snapshot_path=violation.snapshot_path,
        track_id=violation.track_id,
        model_confidence=violation.model_confidence,
        extra_metadata=violation.metadata,
    )
    db.add(db_violation)
    db.commit()
    db.refresh(db_violation)
    return db_violation


def update_violation(
    db: Session, 
    violation_id: int, 
    violation_update: ViolationUpdate,
    user_id: Optional[int] = None
) -> Optional[Violation]:
    """Update violation"""
    db_violation = get_violation(db, violation_id)
    if not db_violation:
        return None
    
    update_data = violation_update.dict(exclude_unset=True)
    
    # Handle status changes
    if "status" in update_data:
        new_status = update_data["status"]
        
        if new_status == ViolationStatus.ACKNOWLEDGED:
            db_violation.acknowledged_by = user_id
            db_violation.acknowledged_at = datetime.utcnow()
        elif new_status == ViolationStatus.RESOLVED:
            db_violation.resolved_by = user_id
            db_violation.resolved_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_violation, field, value)
    
    db.commit()
    db.refresh(db_violation)
    return db_violation


def delete_violation(db: Session, violation_id: int) -> bool:
    """Delete violation"""
    db_violation = get_violation(db, violation_id)
    if not db_violation:
        return False
    
    db.delete(db_violation)
    db.commit()
    return True


def get_violation_stats(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> dict:
    """Get violation statistics"""
    query = db.query(Violation)
    
    if start_date:
        query = query.filter(func.date(Violation.created_at) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Violation.created_at) <= end_date)
    
    total_violations = query.count()
    open_violations = query.filter(Violation.status == ViolationStatus.OPEN).count()
    resolved_violations = query.filter(Violation.status == ViolationStatus.RESOLVED).count()
    
    # Group by type
    type_stats = (
        query.with_entities(Violation.violation_type, func.count(Violation.id))
        .group_by(Violation.violation_type)
        .all()
    )

    rule_stats = (
        query.with_entities(Violation.rule_type, func.count(Violation.id))
        .group_by(Violation.rule_type)
        .all()
    )
    
    # Group by severity
    severity_stats = (
        query.with_entities(Violation.severity, func.count(Violation.id))
        .group_by(Violation.severity)
        .all()
    )
    
    return {
        "total_violations": total_violations,
        "open_violations": open_violations,
        "resolved_violations": resolved_violations,
        "by_type": {str(vtype.value): count for vtype, count in type_stats},
        "by_rule": {str(rtype.value): count for rtype, count in rule_stats if rtype},
        "by_severity": {str(severity.value): count for severity, count in severity_stats}
    }


def get_recent_violations(db: Session, limit: int = 10) -> list[Violation]:
    """Get most recent violations"""
    return (
        db.query(Violation)
        .order_by(Violation.created_at.desc())
        .limit(limit)
        .all()
    )
