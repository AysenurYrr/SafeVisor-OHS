from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import violation as crud_violation
from app.models.user import User
from app.models.violation import ViolationType, ViolationSeverity, ViolationStatus
from app.schemas.violation import (
    ViolationCreate, 
    ViolationUpdate, 
    ViolationResponse,
    ViolationListResponse,
    ViolationStats
)
import os
import uuid

router = APIRouter()


@router.get("/", response_model=ViolationListResponse)
def read_violations(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    employee_id: Optional[int] = Query(None),
    camera_id: Optional[int] = Query(None),
    factory_area_id: Optional[int] = Query(None, alias="area_id"),
    violation_type: Optional[ViolationType] = Query(None),
    severity: Optional[ViolationSeverity] = Query(None),
    status: Optional[ViolationStatus] = Query(None),
    start_date: Optional[date] = Query(None, alias="from"),
    end_date: Optional[date] = Query(None, alias="to"),
    current_user: User = Depends(deps.get_current_active_user),
) -> ViolationListResponse:
    """
    Retrieve violations with optional filters
    """
    violations = crud_violation.get_violations(
        db=db,
        skip=skip,
        limit=limit,
        employee_id=employee_id,
        camera_id=camera_id,
        factory_area_id=factory_area_id,
        violation_type=violation_type,
        severity=severity,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    
    total = crud_violation.count_violations(
        db=db,
        employee_id=employee_id,
        camera_id=camera_id,
        factory_area_id=factory_area_id,
        violation_type=violation_type,
        severity=severity,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    
    return ViolationListResponse(
        violations=violations,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )


@router.post("/", response_model=ViolationResponse)
def create_violation(
    *,
    db: Session = Depends(deps.get_db),
    violation_in: ViolationCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> ViolationResponse:
    """
    Create new violation
    """
    violation = crud_violation.create_violation(db=db, violation=violation_in)
    return violation


@router.post("/with-snapshot", response_model=ViolationResponse)
async def create_violation_with_snapshot(
    *,
    db: Session = Depends(deps.get_db),
    camera_id: int = Form(...),
    factory_area_id: Optional[int] = Form(None),
    employee_id: Optional[int] = Form(None),
    violation_type: str = Form(...),
    rule_type: Optional[str] = Form(None),
    occurred_at: Optional[str] = Form(None),
    confidence_score: int = Form(0),
    person_tracker_id: Optional[int] = Form(None),
    duration_frames: Optional[int] = Form(None),
    snapshot: Optional[UploadFile] = File(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> ViolationResponse:
    """
    Create new violation with snapshot upload (multipart/form-data)
    """
    # Map violation type string to enum
    violation_type_map = {
        'no_helmet': ViolationType.NO_HELMET,
        'no_vest': ViolationType.NO_VEST,
        'no_gloves': ViolationType.NO_GLOVES,
        'no_boots': ViolationType.NO_BOOTS,
        'no_mask': ViolationType.NO_MASK,
        'no_goggles': ViolationType.NO_GOGGLES,
        'glasses': ViolationType.NO_GOGGLES,  # Map GLASSES to NO_GOGGLES
    }
    
    # Use rule_type if provided, otherwise use violation_type
    type_key = (rule_type or violation_type).lower()
    vtype = violation_type_map.get(type_key, ViolationType.INCOMPLETE_PPE)
    
    # Save snapshot if provided
    snapshot_path = None
    if snapshot:
        # Create violations directory
        violations_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'static',
            'violations',
            str(camera_id)
        )
        os.makedirs(violations_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        file_ext = os.path.splitext(snapshot.filename)[1] if snapshot.filename else '.jpg'
        filename = f"{timestamp}_{type_key}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(violations_dir, filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            content = await snapshot.read()
            f.write(content)
        
        # Store relative path for serving
        snapshot_path = f"/static/violations/{camera_id}/{filename}"
    
    # Parse occurred_at timestamp
    occurred_at_dt = None
    if occurred_at:
        try:
            occurred_at_dt = datetime.fromisoformat(occurred_at.replace('Z', '+00:00'))
        except:
            occurred_at_dt = datetime.utcnow()
    else:
        occurred_at_dt = datetime.utcnow()
    
    # Create violation
    violation_in = ViolationCreate(
        camera_id=camera_id,
        factory_area_id=factory_area_id,
        employee_id=employee_id,
        violation_type=vtype,
        occurred_at=occurred_at_dt,
        confidence_score=confidence_score,
        evidence_middle_image=snapshot_path,  # Store snapshot in middle image
        person_tracker_id=person_tracker_id,
        duration_frames=duration_frames,
        description=f"PPE violation: {type_key.replace('_', ' ').title()}"
    )
    
    violation = crud_violation.create_violation(db=db, violation=violation_in)
    return violation


@router.get("/{violation_id}", response_model=ViolationResponse)
def read_violation(
    violation_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ViolationResponse:
    """
    Get a specific violation by ID
    """
    violation = crud_violation.get_violation(db, violation_id=violation_id)
    if not violation:
        raise HTTPException(
            status_code=404,
            detail="Violation not found"
        )
    
    return violation


@router.put("/{violation_id}", response_model=ViolationResponse)
def update_violation(
    *,
    db: Session = Depends(deps.get_db),
    violation_id: int,
    violation_in: ViolationUpdate,
    current_user: User = Depends(deps.check_hse_expert_access),
) -> ViolationResponse:
    """
    Update a violation (HSE Expert/Manager/Admin only)
    """
    violation = crud_violation.get_violation(db, violation_id=violation_id)
    if not violation:
        raise HTTPException(
            status_code=404,
            detail="Violation not found"
        )
    
    violation = crud_violation.update_violation(
        db=db, 
        violation_id=violation_id, 
        violation_update=violation_in,
        user_id=current_user.id
    )
    return violation


@router.delete("/{violation_id}")
def delete_violation(
    *,
    db: Session = Depends(deps.get_db),
    violation_id: int,
    current_user: User = Depends(deps.check_admin_role),
) -> dict:
    """
    Delete a violation (Admin only)
    """
    violation = crud_violation.get_violation(db, violation_id=violation_id)
    if not violation:
        raise HTTPException(
            status_code=404,
            detail="Violation not found"
        )
    
    success = crud_violation.delete_violation(db, violation_id=violation_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete violation"
        )
    
    return {"message": "Violation deleted successfully"}


@router.get("/stats/summary", response_model=ViolationStats)
def get_violation_stats(
    db: Session = Depends(deps.get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(deps.check_hse_expert_access),
) -> ViolationStats:
    """
    Get violation statistics (HSE Expert/Manager/Admin only)
    """
    stats = crud_violation.get_violation_stats(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return ViolationStats(**stats)


@router.get("/recent/list", response_model=list[ViolationResponse])
def get_recent_violations(
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(deps.get_current_active_user),
) -> list[ViolationResponse]:
    """
    Get recent violations
    """
    return crud_violation.get_recent_violations(db, limit=limit)


@router.post("/{violation_id}/acknowledge")
def acknowledge_violation(
    violation_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.check_hse_expert_access),
) -> dict:
    """
    Acknowledge a violation (HSE Expert/Manager/Admin only)
    """
    violation = crud_violation.get_violation(db, violation_id=violation_id)
    if not violation:
        raise HTTPException(
            status_code=404,
            detail="Violation not found"
        )
    
    if violation.status != ViolationStatus.OPEN:
        raise HTTPException(
            status_code=400,
            detail="Can only acknowledge open violations"
        )
    
    from app.schemas.violation import ViolationUpdate, ViolationStatusEnum
    update_data = ViolationUpdate(status=ViolationStatusEnum.ACKNOWLEDGED)
    
    crud_violation.update_violation(
        db=db,
        violation_id=violation_id,
        violation_update=update_data,
        user_id=current_user.id
    )
    
    return {"message": "Violation acknowledged successfully"}


@router.post("/{violation_id}/resolve")
def resolve_violation(
    violation_id: int,
    resolution_notes: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.check_hse_expert_access),
) -> dict:
    """
    Resolve a violation (HSE Expert/Manager/Admin only)
    """
    violation = crud_violation.get_violation(db, violation_id=violation_id)
    if not violation:
        raise HTTPException(
            status_code=404,
            detail="Violation not found"
        )
    
    if violation.status == ViolationStatus.RESOLVED:
        raise HTTPException(
            status_code=400,
            detail="Violation is already resolved"
        )
    
    from app.schemas.violation import ViolationUpdate, ViolationStatusEnum
    update_data = ViolationUpdate(
        status=ViolationStatusEnum.RESOLVED,
        resolution_notes=resolution_notes
    )
    
    crud_violation.update_violation(
        db=db,
        violation_id=violation_id,
        violation_update=update_data,
        user_id=current_user.id
    )
    
    return {"message": "Violation resolved successfully"}