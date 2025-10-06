from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
import uuid as uuid_lib


def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    """Get employee by ID"""
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employee_by_uuid(db: Session, employee_uuid: str) -> Optional[Employee]:
    """Get employee by UUID"""
    try:
        # Handle both string and UUID types
        if isinstance(employee_uuid, str):
            uuid_obj = uuid_lib.UUID(employee_uuid)
        else:
            uuid_obj = employee_uuid
        return db.query(Employee).filter(Employee.uuid == uuid_obj).first()
    except (ValueError, TypeError):
        return None


def get_employee_by_employee_id(db: Session, employee_id: str) -> Optional[Employee]:
    """Get employee by employee_id string"""
    return db.query(Employee).filter(Employee.employee_id == employee_id).first()


def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
    """Get employee by email"""
    return db.query(Employee).filter(Employee.email == email).first()


def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = None,
    position: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> list[Employee]:
    """Get multiple employees with optional filters"""
    query = db.query(Employee)
    
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    
    if position:
        query = query.filter(Employee.position.ilike(f"%{position}%"))
    
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    
    if search:
        search_filter = or_(
            Employee.first_name.ilike(f"%{search}%"),
            Employee.last_name.ilike(f"%{search}%"),
            Employee.employee_id.ilike(f"%{search}%"),
            Employee.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.offset(skip).limit(limit).all()


def count_employees(
    db: Session,
    department: Optional[str] = None,
    position: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> int:
    """Count employees with optional filters"""
    query = db.query(Employee)
    
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    
    if position:
        query = query.filter(Employee.position.ilike(f"%{position}%"))
    
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    
    if search:
        search_filter = or_(
            Employee.first_name.ilike(f"%{search}%"),
            Employee.last_name.ilike(f"%{search}%"),
            Employee.employee_id.ilike(f"%{search}%"),
            Employee.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.count()


def create_employee(db: Session, employee: EmployeeCreate, created_by: int) -> Employee:
    """Create new employee"""
    db_employee = Employee(
        employee_id=employee.employee_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        phone=employee.phone,
        department=employee.department,
        position=employee.position,
        hire_date=employee.hire_date,
        birth_date=employee.birth_date,
        emergency_contact=employee.emergency_contact,
        emergency_phone=employee.emergency_phone,
        photo_url=employee.photo_url,
        photo_front_path=employee.photo_front_path,
        photo_left_path=employee.photo_left_path,
        photo_right_path=employee.photo_right_path,
        face_encoding=employee.face_encoding,
        violation_score=employee.violation_score,
        is_active=employee.is_active,
        notes=employee.notes,
        created_by=created_by
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(
    db: Session, 
    employee_id: int, 
    employee_update: EmployeeUpdate
) -> Optional[Employee]:
    """Update employee"""
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return None
    
    update_data = employee_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: int) -> bool:
    """Delete employee (soft delete by setting is_active to False)"""
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return False
    
    db_employee.is_active = False
    db.commit()
    return True


def get_departments(db: Session) -> list[str]:
    """Get all unique departments"""
    result = db.query(Employee.department).distinct().all()
    return [dept[0] for dept in result if dept[0]]


def get_positions(db: Session) -> list[str]:
    """Get all unique positions"""
    result = db.query(Employee.position).distinct().all()
    return [pos[0] for pos in result if pos[0]]