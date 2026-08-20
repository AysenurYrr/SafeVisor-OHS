from typing import Optional, Any
from datetime import date, datetime
import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import violation as crud_violation
from app.models.user import User
from app.models.violation import ViolationType, ViolationSeverity, ViolationStatus
from app.models.safety_rule import SafetyRuleType
from app.schemas.violation import (
    ViolationCreate, 
    ViolationUpdate, 
    ViolationResponse,
    ViolationListResponse,
    ViolationStats
)

router = APIRouter()


def _map_rule_to_violation(rule_type: Optional[SafetyRuleType]) -> ViolationType:
    mapping = {
        SafetyRuleType.HELMET: ViolationType.NO_HELMET,
        SafetyRuleType.VEST: ViolationType.NO_VEST,
        SafetyRuleType.GLOVES: ViolationType.NO_GLOVES,
        SafetyRuleType.BOOTS: ViolationType.NO_BOOTS,
        SafetyRuleType.GLASSES: ViolationType.NO_GOGGLES,
        SafetyRuleType.MASK: ViolationType.NO_MASK,
    }
    if rule_type and rule_type in mapping:
        return mapping[rule_type]
    return ViolationType.INCOMPLETE_PPE


def _ensure_snapshot_url(violation: Any) -> None:
    """Populate snapshot_url attribute from snapshot_path for response models."""
    snapshot_path = getattr(violation, "snapshot_path", None)
    if snapshot_path and not getattr(violation, "snapshot_url", None):
        try:
            setattr(violation, "snapshot_url", snapshot_path)
        except Exception:
            pass


@router.get("/", response_model=ViolationListResponse)
def read_violations(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    employee_id: Optional[int] = Query(None),
    camera_id: Optional[int] = Query(None),
    factory_area_id: Optional[int] = Query(None),
    violation_type: Optional[ViolationType] = Query(None),
    rule_type: Optional[SafetyRuleType] = Query(None),
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
        factory_area_id=factory_area_id,
        violation_type=violation_type,
        rule_type=rule_type,
        severity=severity,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    for v in violations:
        _ensure_snapshot_url(v)
    
    total = crud_violation.count_violations(
        db=db,
        employee_id=employee_id,
        camera_id=camera_id,
        factory_area_id=factory_area_id,
        violation_type=violation_type,
        rule_type=rule_type,
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
    _ensure_snapshot_url(violation)
    return violation


@router.post("/with-snapshot", response_model=ViolationResponse, status_code=status.HTTP_201_CREATED)
async def create_violation_with_snapshot(
    *,
    db: Session = Depends(deps.get_db),
    camera_id: int = Form(...),
    factory_area_id: Optional[int] = Form(None),
    employee_id: Optional[int] = Form(None),
    rule_type: SafetyRuleType = Form(...),
    occurred_at: Optional[str] = Form(None),
    track_id: Optional[int] = Form(None),
    violation_type: Optional[ViolationType] = Form(None),
    model_confidence: Optional[float] = Form(None),
    metadata: Optional[str] = Form(None),
    snapshot: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> ViolationResponse:
    """
    Create a violation along with an evidence snapshot.
    """
    timestamp = datetime.utcnow()
    if occurred_at:
        try:
            timestamp = datetime.fromisoformat(occurred_at)
        except Exception:
            timestamp = datetime.utcnow()

    violations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "violations", str(camera_id))
    os.makedirs(violations_dir, exist_ok=True)
    safe_rule_value = rule_type.value if hasattr(rule_type, "value") else str(rule_type)
    filename = f"{int(timestamp.timestamp())}_{safe_rule_value}.jpg"
    full_path = os.path.join(violations_dir, filename)

    file_bytes = await snapshot.read()
    with open(full_path, "wb") as f:
        f.write(file_bytes)

    snapshot_url = f"/static/violations/{camera_id}/{filename}"

    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            metadata_dict = None

    violation_payload = ViolationCreate(
        camera_id=camera_id,
        factory_area_id=factory_area_id,
        employee_id=employee_id,
        rule_type=rule_type,
        violation_type=violation_type or _map_rule_to_violation(rule_type),
        description=f"{safe_rule_value} rule violated",
        occurred_at=timestamp,
        snapshot_path=snapshot_url,
        track_id=track_id,
        model_confidence=model_confidence,
        metadata=metadata_dict,
        severity=ViolationSeverity.MEDIUM,
        status=ViolationStatus.OPEN,
        confidence_score=int((model_confidence or 0) * 100),
    )

    violation = crud_violation.create_violation(db=db, violation=violation_payload)
    violation.snapshot_url = snapshot_url  # type: ignore[attr-defined]
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
    
    _ensure_snapshot_url(violation)
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
    if violation:
        _ensure_snapshot_url(violation)
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
    violations = crud_violation.get_recent_violations(db, limit=limit)
    for v in violations:
        _ensure_snapshot_url(v)
    return violations


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
