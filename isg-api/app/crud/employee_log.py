from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.employee_log import EmployeeLog
from app.models.employee import Employee
from app.models.user import User
from app.schemas.employee_log import EmployeeLogCreate


def get_employee_log(db: Session, log_id: int) -> Optional[EmployeeLog]:
    """Get employee log by ID"""
    return db.query(EmployeeLog).filter(EmployeeLog.id == log_id).first()


def get_employee_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[int] = None,
    action: Optional[str] = None
) -> List[EmployeeLog]:
    """Get employee logs with optional filters"""
    query = db.query(EmployeeLog)
    
    if employee_id is not None:
        query = query.filter(EmployeeLog.employee_id == employee_id)
    
    if action:
        query = query.filter(EmployeeLog.action == action)
    
    return query.order_by(EmployeeLog.timestamp.desc()).offset(skip).limit(limit).all()


def count_employee_logs(
    db: Session,
    employee_id: Optional[int] = None,
    action: Optional[str] = None
) -> int:
    """Count employee logs with optional filters"""
    query = db.query(EmployeeLog)
    
    if employee_id is not None:
        query = query.filter(EmployeeLog.employee_id == employee_id)
    
    if action:
        query = query.filter(EmployeeLog.action == action)
    
    return query.count()


def create_employee_log(db: Session, employee_log: EmployeeLogCreate) -> EmployeeLog:
    """Create new employee log"""
    db_log = EmployeeLog(
        employee_id=employee_log.employee_id,
        action=employee_log.action,
        actor_id=employee_log.actor_id,
        details=employee_log.details
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def log_employee_action(
    db: Session,
    employee_id: int,
    action: str,
    actor_id: Optional[int] = None,
    details: Optional[dict] = None
) -> EmployeeLog:
    """Utility function to log an employee action"""
    log = EmployeeLogCreate(
        employee_id=employee_id,
        action=action,
        actor_id=actor_id,
        details=details
    )
    return create_employee_log(db, log)


def get_employee_log_with_names(db: Session, log_id: int) -> Optional[EmployeeLog]:
    """Get employee log with actor and employee names"""
    log = get_employee_log(db, log_id)
    if not log:
        return None
    
    # Add names as attributes
    if log.actor_id:
        actor = db.query(User).filter(User.id == log.actor_id).first()
        log.actor_name = actor.full_name if actor else None
    else:
        log.actor_name = "System"
    
    if log.employee_id:
        employee = db.query(Employee).filter(Employee.id == log.employee_id).first()
        log.employee_name = f"{employee.first_name} {employee.last_name}" if employee else None
    else:
        log.employee_name = None
    
    return log
