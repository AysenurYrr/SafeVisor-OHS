from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.position import Position
from app.models.employee import Employee
from app.models.department import Department
from app.schemas.position import PositionCreate, PositionUpdate


def get_position(db: Session, position_id: int) -> Optional[Position]:
    """Get position by ID"""
    return db.query(Position).filter(Position.id == position_id).first()


def get_position_by_name_and_department(
    db: Session,
    name: str,
    department_id: Optional[int] = None
) -> Optional[Position]:
    """Get position by name and department"""
    query = db.query(Position).filter(Position.name == name)
    if department_id:
        query = query.filter(Position.department_id == department_id)
    return query.first()


def get_positions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> List[Position]:
    """Get multiple positions with optional filters"""
    query = db.query(Position)
    
    if department_id is not None:
        query = query.filter(Position.department_id == department_id)
    
    if is_active is not None:
        query = query.filter(Position.is_active == is_active)
    
    if search:
        query = query.filter(Position.name.ilike(f"%{search}%"))
    
    return query.offset(skip).limit(limit).all()


def count_positions(
    db: Session,
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> int:
    """Count positions with optional filters"""
    query = db.query(Position)
    
    if department_id is not None:
        query = query.filter(Position.department_id == department_id)
    
    if is_active is not None:
        query = query.filter(Position.is_active == is_active)
    
    if search:
        query = query.filter(Position.name.ilike(f"%{search}%"))
    
    return query.count()


def create_position(db: Session, position: PositionCreate) -> Position:
    """Create new position"""
    db_position = Position(
        name=position.name,
        description=position.description,
        department_id=position.department_id,
        is_active=position.is_active
    )
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position


def update_position(
    db: Session,
    position_id: int,
    position_update: PositionUpdate
) -> Optional[Position]:
    """Update position"""
    db_position = get_position(db, position_id)
    if not db_position:
        return None
    
    update_data = position_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_position, field, value)
    
    db.commit()
    db.refresh(db_position)
    return db_position


def delete_position(db: Session, position_id: int) -> bool:
    """Delete a position (soft delete by setting is_active=False)"""
    db_position = get_position(db, position_id)
    if not db_position:
        return False
    
    # Check if position has employees
    employee_count = db.query(Employee).filter(Employee.position_id == position_id).count()
    if employee_count > 0:
        # Soft delete - just mark as inactive
        db_position.is_active = False
        db.commit()
    else:
        # Hard delete if no employees
        db.delete(db_position)
        db.commit()
    
    return True


def get_position_with_counts(db: Session, position_id: int) -> Optional[Position]:
    """Get position with employee count and department name"""
    position = get_position(db, position_id)
    if not position:
        return None
    
    # Add counts and related data as attributes
    position.employee_count = db.query(Employee).filter(Employee.position_id == position_id).count()
    
    if position.department_id:
        department = db.query(Department).filter(Department.id == position.department_id).first()
        position.department_name = department.name if department else None
    else:
        position.department_name = None
    
    return position
