from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
import os
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
from app.models.employee import Employee, EmployeePhoto

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
    
    # Role-based response filtering
    # Map to include computed fields
    enriched = []
    from datetime import datetime
    for e in employees:
        e2 = filter_employee_for_role(e, current_user)
        # Simple status heuristic based on is_active
        e2.status = "active" if getattr(e2, "is_active", True) else "inactive"
        # Placeholder last_activity; in real system, use last pose/violation/etc.
        e2.last_activity = e2.updated_at.isoformat() if getattr(e2, "updated_at", None) else "Never"
        enriched.append(e2)

    return EmployeeListResponse(
        employees=enriched,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )


@router.post("/", response_model=EmployeeResponse)
def create_employee(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.check_manager_or_admin_role),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    hire_date: Optional[str] = Form(None),
    birth_date: Optional[str] = Form(None),
    photo1: Optional[UploadFile] = File(None),
    photo2: Optional[UploadFile] = File(None),
    photo3: Optional[UploadFile] = File(None),
) -> EmployeeResponse:
    """
    Create new employee (Manager/Admin only)
    """
    # Email uniqueness
    existing = crud_employee.get_employee_by_email(db, email=email)
    if existing:
        raise HTTPException(status_code=400, detail="Employee with this email already exists in the system.")

    # Build minimal create payload using existing schema
    from datetime import date
    emp_create = EmployeeCreate(
        employee_id=f"EM-{int(os.urandom(3).hex(), 16)}",  # temporary ID
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        department=department or "",
        position=position or "",
        hire_date=date.today(),
        birth_date=None,
        face_encoding=None,
        is_active=True,
        notes=None,
    )

    employee = crud_employee.create_employee(
        db=db, employee=emp_create, created_by=current_user.id
    )

    # Save up to 3 photos
    save_employee_photos(db, employee, [photo1, photo2, photo3])
    return filter_employee_for_role(employee, current_user)


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
    
    return filter_employee_for_role(employee, current_user)


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
    return filter_employee_for_role(employee, current_user)


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


# Helpers
def filter_employee_for_role(employee: Employee, current_user: User) -> Employee:
    # Normalize current user roles
    role_names = set()
    if current_user.role and current_user.role.name:
        role_names.add(current_user.role.name.upper())
    if getattr(current_user, "roles", None):
        for r in current_user.roles:
            if r and r.name:
                role_names.add(r.name.upper())

    # ADMIN/MANAGER: full
    if "ADMIN" in role_names or "MANAGER" in role_names:
        return employee

    # HSE_EXPERT: mask phone and position only
    if "HSE_EXPERT" in role_names:
        employee.phone = None
        employee.position = None
        return employee

    # IT_ADMIN: mask phone, position, and hide photos
    if "IT_ADMIN" in role_names:
        employee.phone = None
        employee.position = None
        # Do not include photos in response
        employee.photos = []
        return employee

    # Others: forbidden
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def save_employee_photos(db: Session, employee: Employee, files: List[Optional[UploadFile]]):
    # Filter valid files (max 3)
    valid_files = [f for f in files if f is not None][:3]
    if not valid_files:
        return
    # Directory: app/static/employees/{employee_id}
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static", "employees", str(employee.id))
    base_dir = os.path.abspath(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    # Clear existing photos beyond 3
    if employee.photos:
        for p in list(employee.photos):
            try:
                if p.file_path and os.path.exists(p.file_path):
                    os.remove(p.file_path)
            except Exception:
                pass
            db.delete(p)
        db.commit()
        employee.photos = []
    # Save each file
    for idx, upload in enumerate(valid_files, start=1):
        ext = os.path.splitext(upload.filename or "")[1] or ".jpg"
        filename = f"photo{idx}{ext}"
        destination = os.path.join(base_dir, filename)
        with open(destination, "wb") as out:
            out.write(upload.file.read())
        # Store relative URL so frontend can load via /static
        rel_path = os.path.relpath(destination, os.path.join(os.path.dirname(__file__), "..", "..", "static"))
        photo = EmployeePhoto(employee_id=employee.id, file_path=os.path.join("/static", rel_path.replace("\\", "/")))
        db.add(photo)
    db.commit()