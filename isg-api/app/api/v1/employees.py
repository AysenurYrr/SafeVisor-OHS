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
from app.services.face_embedding_service import generate_employee_embedding

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
    current_user: User = Depends(deps.check_admin_role),  # Only Admin can create
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    hire_date: Optional[str] = Form(None),
    birth_date: Optional[str] = Form(None),
    emergency_contact: Optional[str] = Form(None),
    emergency_phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    photo_front: UploadFile = File(...),  # Required
    photo_left: UploadFile = File(...),   # Required
    photo_right: UploadFile = File(...),  # Required
) -> EmployeeResponse:
    """
    Create new employee (Admin only)
    Requires 3 photos: front, left, and right profile
    """
    # Basic email format validation
    def _validate_email(value: str):
        if not value or '@' not in value or value.count('@') != 1:
            raise HTTPException(status_code=422, detail="Invalid email format")
        local, domain = value.split('@', 1)
        if not local or not domain or '.' not in domain:
            raise HTTPException(status_code=422, detail="Invalid email format")
        if domain.startswith('.') or domain.endswith('.'):
            raise HTTPException(status_code=422, detail="Invalid email format")

    _validate_email(email)

    # Validate that all 3 photos are provided
    if not photo_front or not photo_left or not photo_right:
        raise HTTPException(
            status_code=422,
            detail="All three photos (front, left, right) are required"
        )
    
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
        hire_date=date.today() if not hire_date else date.fromisoformat(hire_date),
        birth_date=date.fromisoformat(birth_date) if birth_date else None,
        emergency_contact=emergency_contact,
        emergency_phone=emergency_phone,
        face_encoding=None,
        violation_score=0,
        is_active=True,
        notes=notes,
    )

    employee = crud_employee.create_employee(
        db=db, employee=emp_create, created_by=current_user.id
    )

    # Save the 3 required photos
    save_employee_photos_required(db, employee, photo_front, photo_left, photo_right)

    # Refresh to get updated photo paths
    db.refresh(employee)

    # Attempt face embedding generation (best-effort)
    try:
        static_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
        photo_relatives = [employee.photo_front_path, employee.photo_left_path, employee.photo_right_path]
        photo_fs_paths = []
        for rel in photo_relatives:
            if rel and rel.startswith('/static/'):
                abs_path = os.path.join(static_root, rel[len('/static/'):].lstrip('/'))
                photo_fs_paths.append(abs_path)
        embedding = generate_employee_embedding(employee.id, photo_fs_paths)
        if embedding:
            employee.face_embedding = embedding
            db.add(employee)
            db.commit()
            db.refresh(employee)
    except Exception as e:  # pragma: no cover
        import logging
        logging.getLogger("app.employees.create").warning("Failed to generate face embedding for employee_id=%s: %s", employee.id, e)

    return filter_employee_for_role(employee, current_user)


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
    current_user: User = Depends(deps.check_admin_role),  # Only Admin can update
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    hire_date: Optional[str] = Form(None),
    birth_date: Optional[str] = Form(None),
    emergency_contact: Optional[str] = Form(None),
    emergency_phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    photo_front: Optional[UploadFile] = File(None),
    photo_left: Optional[UploadFile] = File(None),
    photo_right: Optional[UploadFile] = File(None),
) -> EmployeeResponse:
    """
    Update an employee by UUID (Admin only)
    Photos can be optionally updated
    """
    employee = crud_employee.get_employee_by_uuid(db, employee_uuid=employee_uuid)
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )
    
    # Build update dict from form data
    update_data = {}
    if first_name is not None:
        update_data['first_name'] = first_name
    if last_name is not None:
        update_data['last_name'] = last_name
    if email is not None:
        # Validate email format if provided
        def _validate_email(value: str):
            if not value or '@' not in value or value.count('@') != 1:
                raise HTTPException(status_code=422, detail="Invalid email format")
            local, domain = value.split('@', 1)
            if not local or not domain or '.' not in domain:
                raise HTTPException(status_code=422, detail="Invalid email format")
            if domain.startswith('.') or domain.endswith('.'):
                raise HTTPException(status_code=422, detail="Invalid email format")
        _validate_email(email)
        # Check email uniqueness if updating email
        if email != employee.email:
            existing_employee = crud_employee.get_employee_by_email(db, email=email)
            if existing_employee:
                raise HTTPException(
                    status_code=400,
                    detail="Employee with this email already exists"
                )
        update_data['email'] = email
    if phone is not None:
        update_data['phone'] = phone
    if position is not None:
        update_data['position'] = position
    if department is not None:
        update_data['department'] = department
    if hire_date is not None:
        from datetime import date
        update_data['hire_date'] = date.fromisoformat(hire_date)
    if birth_date is not None:
        from datetime import date
        update_data['birth_date'] = date.fromisoformat(birth_date)
    if emergency_contact is not None:
        update_data['emergency_contact'] = emergency_contact
    if emergency_phone is not None:
        update_data['emergency_phone'] = emergency_phone
    if notes is not None:
        update_data['notes'] = notes
    if is_active is not None:
        update_data['is_active'] = is_active
    
    # Apply updates
    if update_data:
        employee_update = EmployeeUpdate(**update_data)
        employee = crud_employee.update_employee(
            db=db, employee_id=employee.id, employee_update=employee_update
        )
    
    # Update photos if provided (and recompute embedding)
    if photo_front or photo_left or photo_right:
        update_employee_photos(db, employee, photo_front, photo_left, photo_right)
        db.refresh(employee)
        # Recompute embedding
        try:
            static_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static"))
            photo_relatives = [employee.photo_front_path, employee.photo_left_path, employee.photo_right_path]
            photo_fs_paths = []
            for rel in photo_relatives:
                if rel and rel.startswith('/static/'):
                    abs_path = os.path.join(static_root, rel[len('/static/'):].lstrip('/'))
                    photo_fs_paths.append(abs_path)
            embedding = generate_employee_embedding(employee.id, photo_fs_paths)
            if embedding:
                employee.face_embedding = embedding
                db.add(employee)
                db.commit()
                db.refresh(employee)
        except Exception as e:  # pragma: no cover
            import logging
            logging.getLogger("app.employees.update").warning("Failed to regenerate face embedding for employee_id=%s: %s", employee.id, e)
    
    return filter_employee_for_role(employee, current_user)


@router.delete("/{employee_uuid}")
def delete_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_uuid: str,
    current_user: User = Depends(deps.check_admin_role),  # Only Admin can delete
) -> dict:
    """
    Delete an employee by UUID (Admin only)
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

    return {"message": "Employee deleted successfully", "deleted": True, "employee_uuid": employee_uuid}


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


@router.post("/seed")
def seed_employees(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.check_admin_role),
    count: int = Query(5, ge=1, le=20, description="Number of sample employees to create")
) -> dict:
    """
    Seed sample employees with placeholder photos (Admin only)
    Creates dummy employees for testing purposes
    """
    import requests
    from datetime import date, timedelta
    import random
    
    # Sample data
    first_names = ["John", "Jane", "Mike", "Sarah", "David", "Emily", "Robert", "Lisa", "James", "Maria"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    departments = ["Manufacturing", "Safety", "Quality Control", "Maintenance", "Engineering"]
    positions = ["Supervisor", "Technician", "Inspector", "Specialist", "Manager"]
    
    created_employees = []
    
    for i in range(count):
        # Generate random employee data
        first = random.choice(first_names)
        last = random.choice(last_names)
        email = f"{first.lower()}.{last.lower()}.{random.randint(100, 999)}@company.com"
        
        # Check if email already exists
        existing = crud_employee.get_employee_by_email(db, email=email)
        if existing:
            continue
        
        emp_create = EmployeeCreate(
            employee_id=f"EM-{random.randint(1000, 9999)}",
            first_name=first,
            last_name=last,
            email=email,
            phone=f"+1-555-{random.randint(1000, 9999)}",
            department=random.choice(departments),
            position=random.choice(positions),
            hire_date=date.today() - timedelta(days=random.randint(30, 1095)),
            birth_date=date.today() - timedelta(days=random.randint(7300, 18250)),
            emergency_contact=f"{random.choice(first_names)} {random.choice(last_names)}",
            emergency_phone=f"+1-555-{random.randint(1000, 9999)}",
            violation_score=random.randint(0, 5),
            is_active=True,
            notes="Sample employee created by seed function"
        )
        
        # Create employee
        employee = crud_employee.create_employee(
            db=db, employee=emp_create, created_by=current_user.id
        )
        
        # Create placeholder photos directory
        base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static", "employees", str(employee.id))
        os.makedirs(base_dir, exist_ok=True)
        
        # Download placeholder images from a free service
        photo_types = ["front", "left", "right"]
        for photo_type in photo_types:
            try:
                # Use a placeholder image service (thispersondoesnotexist.com or similar)
                # For now, create a simple placeholder
                placeholder_path = os.path.join(base_dir, f"{photo_type}.jpg")
                
                # Try to download from placeholder service
                try:
                    response = requests.get(
                        f"https://i.pravatar.cc/300?img={random.randint(1, 70)}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        with open(placeholder_path, "wb") as f:
                            f.write(response.content)
                    else:
                        # Fallback: create a colored placeholder
                        _create_placeholder_image(placeholder_path, photo_type)
                except Exception:
                    # Fallback: create a colored placeholder
                    _create_placeholder_image(placeholder_path, photo_type)
                
                # Update employee with photo path
                rel_path = os.path.relpath(placeholder_path, os.path.join(os.path.dirname(__file__), "..", "..", "static"))
                photo_path = f"/static/{rel_path.replace(os.sep, '/')}"
                
                if photo_type == "front":
                    employee.photo_front_path = photo_path
                elif photo_type == "left":
                    employee.photo_left_path = photo_path
                elif photo_type == "right":
                    employee.photo_right_path = photo_path
            except Exception as e:
                print(f"Failed to create placeholder photo for {photo_type}: {e}")
        
        db.commit()
        db.refresh(employee)
        created_employees.append(employee)
    
    return {
        "message": f"Successfully created {len(created_employees)} sample employees",
        "count": len(created_employees),
        "employee_ids": [e.id for e in created_employees]
    }


def _create_placeholder_image(path: str, photo_type: str):
    """Create a simple colored placeholder image"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a colored image based on type
        colors = {
            "front": (100, 149, 237),  # Cornflower blue
            "left": (144, 238, 144),   # Light green
            "right": (255, 182, 193),  # Light pink
        }
        
        img = Image.new('RGB', (300, 300), color=colors.get(photo_type, (200, 200, 200)))
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = photo_type.upper()
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((300 - text_width) // 2, (300 - text_height) // 2)
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        img.save(path)
    except Exception as e:
        # If PIL is not available, create a minimal file
        with open(path, "wb") as f:
            # Write a minimal valid JPEG (1x1 pixel)
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfe\xfe\xa2\x8a\x00(\xa2\x8a\x00\xff\xd9')


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


def save_employee_photos_required(db: Session, employee: Employee, photo_front: UploadFile, photo_left: UploadFile, photo_right: UploadFile):
    """
    Save the 3 required photos for an employee.
    Stores them in /app/static/employees/{employee_id}/ and updates the database paths.
    """
    # Directory: app/static/employees/{employee_id}
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static", "employees", str(employee.id))
    base_dir = os.path.abspath(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    
    # Helper to save a photo and return its URL path
    def save_photo(upload_file: UploadFile, photo_type: str) -> str:
        ext = os.path.splitext(upload_file.filename or "")[1] or ".jpg"
        filename = f"{photo_type}{ext}"
        destination = os.path.join(base_dir, filename)
        
        # Write file
        with open(destination, "wb") as out:
            out.write(upload_file.file.read())
        
        # Return URL path (relative to /static)
        rel_path = os.path.relpath(destination, os.path.join(os.path.dirname(__file__), "..", "..", "static"))
        return f"/static/{rel_path.replace(os.sep, '/')}"
    
    # Save each photo and update employee record
    employee.photo_front_path = save_photo(photo_front, "front")
    employee.photo_left_path = save_photo(photo_left, "left")
    employee.photo_right_path = save_photo(photo_right, "right")
    
    db.commit()


def update_employee_photos(db: Session, employee: Employee, photo_front: Optional[UploadFile], photo_left: Optional[UploadFile], photo_right: Optional[UploadFile]):
    """
    Update employee photos. Only updates the photos that are provided.
    """
    # Directory: app/static/employees/{employee_id}
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static", "employees", str(employee.id))
    base_dir = os.path.abspath(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    
    # Helper to save a photo and return its URL path
    def save_photo(upload_file: UploadFile, photo_type: str) -> str:
        ext = os.path.splitext(upload_file.filename or "")[1] or ".jpg"
        filename = f"{photo_type}{ext}"
        destination = os.path.join(base_dir, filename)
        
        # Delete old file if exists
        if os.path.exists(destination):
            try:
                os.remove(destination)
            except Exception:
                pass
        
        # Write new file
        with open(destination, "wb") as out:
            out.write(upload_file.file.read())
        
        # Return URL path (relative to /static)
        rel_path = os.path.relpath(destination, os.path.join(os.path.dirname(__file__), "..", "..", "static"))
        return f"/static/{rel_path.replace(os.sep, '/')}"
    
    # Update only the photos that were provided
    if photo_front:
        employee.photo_front_path = save_photo(photo_front, "front")
    if photo_left:
        employee.photo_left_path = save_photo(photo_left, "left")
    if photo_right:
        employee.photo_right_path = save_photo(photo_right, "right")
    
    db.commit()


def save_employee_photos(db: Session, employee: Employee, files: List[Optional[UploadFile]]):
    """
    Legacy function for backward compatibility - saves up to 3 photos.
    Deprecated: Use save_employee_photos_required for new employees.
    """
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