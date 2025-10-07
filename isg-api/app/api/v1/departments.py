from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import department as crud_department
from app.models.user import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)

router = APIRouter()


@router.get("/", response_model=List[DepartmentResponse])
def read_departments(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[DepartmentResponse]:
    """
    Retrieve departments with optional filters
    """
    departments = crud_department.get_departments(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search
    )
    
    # Add counts to each department
    result = []
    for dept in departments:
        dept_with_counts = crud_department.get_department_with_counts(db, dept.id)
        result.append(dept_with_counts)
    
    return result


@router.post("/", response_model=DepartmentResponse)
def create_department(
    *,
    db: Session = Depends(deps.get_db),
    department: DepartmentCreate,
    current_user: User = Depends(deps.check_admin_role),  # Only Admin can create
) -> DepartmentResponse:
    """
    Create new department (Admin only)
    """
    # Check if department with same name already exists
    existing = crud_department.get_department_by_name(db, name=department.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Department with this name already exists"
        )
    
    db_department = crud_department.create_department(db=db, department=department)
    return crud_department.get_department_with_counts(db, db_department.id)


@router.get("/{department_id}", response_model=DepartmentResponse)
def read_department(
    department_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> DepartmentResponse:
    """
    Get a specific department by ID
    """
    department = crud_department.get_department_with_counts(db, department_id=department_id)
    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )
    
    return department


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    *,
    db: Session = Depends(deps.get_db),
    department_id: int,
    department_update: DepartmentUpdate,
    current_user: User = Depends(deps.check_admin_role),  # Only Admin can update
) -> DepartmentResponse:
    """
    Update a department by ID (Admin only)
    """
    department = crud_department.get_department(db, department_id=department_id)
    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )
    
    # Check name uniqueness if updating name
    if department_update.name and department_update.name != department.name:
        existing_department = crud_department.get_department_by_name(db, name=department_update.name)
        if existing_department:
            raise HTTPException(
                status_code=400,
                detail="Department with this name already exists"
            )
    
    updated_department = crud_department.update_department(
        db=db, department_id=department_id, department_update=department_update
    )
    
    return crud_department.get_department_with_counts(db, updated_department.id)


@router.delete("/{department_id}")
def delete_department(
    *,
    db: Session = Depends(deps.get_db),
    department_id: int,
    current_user: User = Depends(deps.check_admin_role),  # Only Admin can delete
) -> dict:
    """
    Delete a department by ID (Admin only)
    If department has employees, it will be soft deleted (marked as inactive)
    """
    department = crud_department.get_department(db, department_id=department_id)
    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )
    
    success = crud_department.delete_department(db, department_id=department_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete department"
        )
    
    return {
        "message": "Department deleted successfully",
        "deleted": True,
        "department_id": department_id
    }
