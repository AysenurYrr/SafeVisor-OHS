from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud import violation_log
from app.schemas.violation_log import (
    ViolationLogResponse, 
    ViolationLogCreate,
    ViolationLogUpdate,
    ViolationLogListResponse
)
from app.api.deps import get_current_active_user
from app.models.user import User
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=ViolationLogListResponse)
async def get_violation_logs(
    skip: int = Query(0, ge=0, description="Skip number of records"),
    limit: int = Query(100, ge=1, le=100, description="Limit number of records"),
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    camera_id: Optional[int] = Query(None, description="Filter by camera ID"),
    reported: Optional[bool] = Query(None, description="Filter by reported status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start datetime"),
    end_date: Optional[datetime] = Query(None, description="Filter by end datetime"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get violation logs with filtering options"""
    
    violation_logs = violation_log.violation_log.get_multi(
        db,
        skip=skip,
        limit=limit,
        employee_id=employee_id,
        camera_id=camera_id,
        reported=reported,
        start_date=start_date,
        end_date=end_date
    )
    
    total = violation_log.violation_log.count(
        db,
        employee_id=employee_id,
        camera_id=camera_id,
        reported=reported,
        start_date=start_date,
        end_date=end_date
    )
    
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return ViolationLogListResponse(
        violation_logs=violation_logs,
        total=total,
        page=page,
        per_page=limit
    )


@router.get("/{violation_log_id}", response_model=ViolationLogResponse)
async def get_violation_log(
    violation_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific violation log by ID"""
    
    violation_log_obj = violation_log.violation_log.get(db, id=violation_log_id)
    if not violation_log_obj:
        raise HTTPException(status_code=404, detail="Violation log not found")
    
    return violation_log_obj


@router.post("/", response_model=ViolationLogResponse)
async def create_violation_log(
    violation_log_create: ViolationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new violation log"""
    
    # Validate that camera exists
    from app.crud import camera
    camera_obj = camera.camera.get(db, id=violation_log_create.camera_id)
    if not camera_obj:
        raise HTTPException(status_code=400, detail="Camera not found")
    
    # Validate employee if provided
    if violation_log_create.employee_id:
        from app.crud import employee
        employee_obj = employee.employee.get(db, id=violation_log_create.employee_id)
        if not employee_obj:
            raise HTTPException(status_code=400, detail="Employee not found")
    
    return violation_log.violation_log.create(db, obj_in=violation_log_create)


@router.put("/{violation_log_id}", response_model=ViolationLogResponse)
async def update_violation_log(
    violation_log_id: int,
    violation_log_update: ViolationLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a violation log"""
    
    violation_log_obj = violation_log.violation_log.get(db, id=violation_log_id)
    if not violation_log_obj:
        raise HTTPException(status_code=404, detail="Violation log not found")
    
    # Validate camera if being updated
    if violation_log_update.camera_id:
        from app.crud import camera
        camera_obj = camera.camera.get(db, id=violation_log_update.camera_id)
        if not camera_obj:
            raise HTTPException(status_code=400, detail="Camera not found")
    
    # Validate employee if being updated
    if violation_log_update.employee_id:
        from app.crud import employee
        employee_obj = employee.employee.get(db, id=violation_log_update.employee_id)
        if not employee_obj:
            raise HTTPException(status_code=400, detail="Employee not found")
    
    return violation_log.violation_log.update(db, db_obj=violation_log_obj, obj_in=violation_log_update)


@router.delete("/{violation_log_id}")
async def delete_violation_log(
    violation_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a violation log"""
    
    violation_log_obj = violation_log.violation_log.get(db, id=violation_log_id)
    if not violation_log_obj:
        raise HTTPException(status_code=404, detail="Violation log not found")
    
    violation_log.violation_log.remove(db, id=violation_log_id)
    return {"message": "Violation log deleted successfully"}