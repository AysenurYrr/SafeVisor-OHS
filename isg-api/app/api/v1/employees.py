from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import employee as crud_employee
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate, 
    EmployeeUpdate, 
    EmployeeResponse,
    EmployeeListResponse
)

router = APIRouter()


@router.get("/", response_model=EmployeeListResponse)
def read_employees(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    department: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> EmployeeListResponse:
    """
    Retrieve employees with optional filters
    """
    employees = crud_employee.get_employees(
        db=db,
        skip=skip,
        limit=limit,
        department=department,
        position=position,
        is_active=is_active,
        search=search
    )
    
    total = crud_employee.count_employees(
        db=db,
        department=department,
        position=position,
        is_active=is_active,
        search=search
    )
    
    return EmployeeListResponse(
        employees=employees,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )


@router.post("/", response_model=EmployeeResponse)
def create_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_in: EmployeeCreate,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> EmployeeResponse:
    """
    Create new employee (Manager/Admin only)
    """
    # Check if employee with employee_id already exists
    employee = crud_employee.get_employee_by_employee_id(
        db, employee_id=employee_in.employee_id
    )
    if employee:
        raise HTTPException(
            status_code=400,
            detail="Employee with this ID already exists in the system.",
        )
    
    # Check if employee with email already exists (if email provided)
    if employee_in.email:
        employee = crud_employee.get_employee_by_email(db, email=employee_in.email)
        if employee:
            raise HTTPException(
                status_code=400,
                detail="Employee with this email already exists in the system.",
            )
    
    employee = crud_employee.create_employee(
        db=db, employee=employee_in, created_by=current_user.id
    )
    return employee


@router.get("/{employee_id}", response_model=EmployeeResponse)
def read_employee(
    employee_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> EmployeeResponse:
    """
    Get a specific employee by ID
    """
    employee = crud_employee.get_employee(db, employee_id=employee_id)
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )
    
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_id: int,
    employee_in: EmployeeUpdate,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> EmployeeResponse:
    """
    Update an employee (Manager/Admin only)
    """
    employee = crud_employee.get_employee(db, employee_id=employee_id)
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )
    
    # Check employee_id uniqueness if updating
    if employee_in.employee_id and employee_in.employee_id != employee.employee_id:
        existing_employee = crud_employee.get_employee_by_employee_id(
            db, employee_id=employee_in.employee_id
        )
        if existing_employee:
            raise HTTPException(
                status_code=400,
                detail="Employee with this ID already exists"
            )
    
    # Check email uniqueness if updating email
    if employee_in.email and employee_in.email != employee.email:
        existing_employee = crud_employee.get_employee_by_email(
            db, email=employee_in.email
        )
        if existing_employee:
            raise HTTPException(
                status_code=400,
                detail="Employee with this email already exists"
            )
    
    employee = crud_employee.update_employee(
        db=db, employee_id=employee_id, employee_update=employee_in
    )
    return employee


@router.delete("/{employee_id}")
def delete_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_id: int,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> dict:
    """
    Delete an employee (Manager/Admin only)
    """
    employee = crud_employee.get_employee(db, employee_id=employee_id)
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )
    
    success = crud_employee.delete_employee(db, employee_id=employee_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete employee"
        )
    
    return {"message": "Employee deleted successfully"}


@router.get("/departments/list")
def get_departments(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[str]:
    """
    Get all unique departments
    """
    return crud_employee.get_departments(db)


@router.get("/positions/list")
def get_positions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[str]:
    """
    Get all unique positions
    """
    return crud_employee.get_positions(db)