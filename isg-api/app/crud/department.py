from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.department import Department
from app.models.employee import Employee
from app.models.position import Position
from app.schemas.department import DepartmentCreate, DepartmentUpdate


def get_department(db: Session, department_id: int) -> Optional[Department]:
    """Get department by ID"""
    return db.query(Department).filter(Department.id == department_id).first()


def get_department_by_name(db: Session, name: str) -> Optional[Department]:
    """Get department by name"""
    return db.query(Department).filter(Department.name == name).first()


def get_departments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> List[Department]:
    """Get multiple departments with optional filters"""
    query = db.query(Department)
    
    if is_active is not None:
        query = query.filter(Department.is_active == is_active)
    
    if search:
        query = query.filter(Department.name.ilike(f"%{search}%"))
    
    return query.offset(skip).limit(limit).all()


def count_departments(
    db: Session,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> int:
    """Count departments with optional filters"""
    query = db.query(Department)
    
    if is_active is not None:
        query = query.filter(Department.is_active == is_active)
    
    if search:
        query = query.filter(Department.name.ilike(f"%{search}%"))
    
    return query.count()


def create_department(db: Session, department: DepartmentCreate) -> Department:
    """Create new department"""
    db_department = Department(
        name=department.name,
        description=department.description,
        is_active=department.is_active
    )
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department


def update_department(
    db: Session,
    department_id: int,
    department_update: DepartmentUpdate
) -> Optional[Department]:
    """Update department"""
    db_department = get_department(db, department_id)
    if not db_department:
        return None
    
    update_data = department_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_department, field, value)
    
    db.commit()
    db.refresh(db_department)
    return db_department


def delete_department(db: Session, department_id: int) -> bool:
    """Delete a department (soft delete by setting is_active=False)"""
    db_department = get_department(db, department_id)
    if not db_department:
        return False
    
    # Check if department has employees
    employee_count = db.query(Employee).filter(Employee.department_id == department_id).count()
    if employee_count > 0:
        # Soft delete - just mark as inactive
        db_department.is_active = False
        db.commit()
    else:
        # Hard delete if no employees
        db.delete(db_department)
        db.commit()
    
    return True


def get_department_with_counts(db: Session, department_id: int) -> Optional[Department]:
    """Get department with employee and position counts"""
    department = get_department(db, department_id)
    if not department:
        return None
    
    # Add counts as attributes
    department.employee_count = db.query(Employee).filter(Employee.department_id == department_id).count()
    department.position_count = db.query(Position).filter(Position.department_id == department_id).count()
    
    return department
