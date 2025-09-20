from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
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

router = APIRouter()


@router.get("/", response_model=ViolationListResponse)
def read_violations(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    employee_id: Optional[int] = Query(None),
    camera_id: Optional[int] = Query(None),
    violation_type: Optional[ViolationType] = Query(None),
    severity: Optional[ViolationSeverity] = Query(None),
    status: Optional[ViolationStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
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