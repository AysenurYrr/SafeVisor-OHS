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


@router.post("/", response_model=EmployeeResponse, status_code=201)
async def create_employee(
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
    employee_id: Optional[str] = Form(None),
    emergency_phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    photo1: Optional[UploadFile] = File(None),
    photo2: Optional[UploadFile] = File(None),
    photo3: Optional[UploadFile] = File(None),
) -> EmployeeResponse:
    """
    Create new employee (Manager/Admin only)
    Accepts multipart/form-data with text fields and up to 3 photo files
    """
    import logging
    logger = logging.getLogger("app.employees")
    
    try:
        # Email uniqueness check
        existing = crud_employee.get_employee_by_email(db, email=email)
        if existing:
            raise HTTPException(
                status_code=400, 
                detail="Employee with this email already exists in the system."
            )

        # Generate employee_id if not provided
        if not employee_id:
            employee_id = f"EM-{int(os.urandom(3).hex(), 16)}"

        # Build minimal create payload using existing schema
        from datetime import date
        emp_create = EmployeeCreate(
            employee_id=employee_id,
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
            notes=notes,
            # Photos will be handled separately via save_employee_photos
            photo_1_path=None,
            photo_2_path=None,
            photo_3_path=None,
        )

        logger.info(f"Creating employee: {first_name} {last_name} ({email})")

        # Create employee record
        employee = crud_employee.create_employee(
            db=db, employee=emp_create, created_by=current_user.id
        )

        # Save up to 3 photos
        try:
            save_employee_photos(db, employee, [photo1, photo2, photo3])
            logger.info(f"Successfully saved photos for employee {employee.id}")
        except Exception as photo_error:
            logger.error(f"Error saving photos for employee {employee.id}: {photo_error}")
            # Don't fail the creation, but log the error
            
        # Refresh to get updated photo paths
        db.refresh(employee)
        
        return filter_employee_for_role(employee, current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating employee: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create employee: {str(e)}"
        )


@router.get("/{employee_uuid}", response_model=EmployeeResponse)
def read_employee(
    employee_uuid: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> EmployeeResponse:
    """
    Get a specific employee by UUID
    """
    employee = crud_employee.get_employee_by_uuid(db, employee_uuid=employee_uuid)
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )
    
    return filter_employee_for_role(employee, current_user)


@router.put("/{employee_uuid}", response_model=EmployeeResponse)
def update_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_uuid: str,
    employee_in: EmployeeUpdate,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> EmployeeResponse:
    """
    Update an employee by UUID (Manager/Admin only)
    """
    employee = crud_employee.get_employee_by_uuid(db, employee_uuid=employee_uuid)
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
        db=db, employee_id=employee.id, employee_update=employee_in
    )
    return filter_employee_for_role(employee, current_user)


@router.delete("/{employee_uuid}")
def delete_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_uuid: str,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> dict:
    """
    Delete an employee by UUID (Manager/Admin only)
    """
    employee = crud_employee.get_employee_by_uuid(db, employee_uuid=employee_uuid)
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )
    
    success = crud_employee.delete_employee(db, employee_id=employee.id)
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
    """
    Save employee photos to /app/static/employees/{employee_id}/
    Updates employee.photos relationship with EmployeePhoto records
    """
    import logging
    logger = logging.getLogger("app.employees")
    
    # Filter valid files (max 3)
    valid_files = [f for f in files if f is not None and f.filename][:3]
    if not valid_files:
        logger.info(f"No photos provided for employee {employee.id}")
        return
        
    # Directory: app/static/employees/{employee_id}
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static", "employees", str(employee.id))
    base_dir = os.path.abspath(base_dir)
    
    try:
        # Create directory with proper permissions
        os.makedirs(base_dir, exist_ok=True)
        logger.info(f"Created/verified directory: {base_dir}")
    except Exception as e:
        logger.error(f"Failed to create directory {base_dir}: {e}")
        raise Exception(f"Failed to create employee photo directory: {e}")
    
    # Clear existing photos
    if employee.photos:
        for p in list(employee.photos):
            try:
                # Extract actual file path (remove /static prefix if present)
                file_path = p.file_path
                if file_path.startswith("/static/"):
                    file_path = os.path.join(
                        os.path.dirname(__file__), "..", "..", "static",
                        file_path.replace("/static/", "")
                    )
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted old photo: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete old photo {p.file_path}: {e}")
            db.delete(p)
        db.commit()
        employee.photos = []
    
    # Save each file
    saved_count = 0
    for idx, upload in enumerate(valid_files, start=1):
        try:
            # Get file extension from filename
            ext = os.path.splitext(upload.filename or "")[1] or ".jpg"
            if not ext.startswith('.'):
                ext = f".{ext}"
            
            filename = f"photo{idx}{ext}"
            destination = os.path.join(base_dir, filename)
            
            # Read and write file
            content = upload.file.read()
            with open(destination, "wb") as out:
                out.write(content)
            
            logger.info(f"Saved photo {idx} to {destination} ({len(content)} bytes)")
            
            # Store relative URL so frontend can load via /static
            rel_path = os.path.relpath(
                destination, 
                os.path.join(os.path.dirname(__file__), "..", "..", "static")
            )
            photo_url = os.path.join("/static", rel_path.replace("\\", "/"))
            
            # Create EmployeePhoto record
            photo = EmployeePhoto(employee_id=employee.id, file_path=photo_url)
            db.add(photo)
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Failed to save photo {idx} for employee {employee.id}: {e}")
            # Continue with other files
            
    try:
        db.commit()
        logger.info(f"Successfully saved {saved_count} photos for employee {employee.id}")
    except Exception as e:
        logger.error(f"Failed to commit photo records: {e}")
        db.rollback()
        raise