from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import position as crud_position
from app.models.user import User
from app.schemas.position import (
    PositionCreate,
    PositionUpdate,
    PositionResponse
)

router = APIRouter()


@router.get("/", response_model=List[PositionResponse])
def read_positions(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    department_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[PositionResponse]:
    """
    Retrieve positions with optional filters
    """
    positions = crud_position.get_positions(
        db=db,
        skip=skip,
        limit=limit,
        department_id=department_id,
        is_active=is_active,
        search=search
    )
    
    # Add counts and department names to each position
    result = []
    for pos in positions:
        pos_with_counts = crud_position.get_position_with_counts(db, pos.id)
        result.append(pos_with_counts)
    
    return result


@router.post("/", response_model=PositionResponse)
def create_position(
    *,
    db: Session = Depends(deps.get_db),
    position: PositionCreate,
    current_user: User = Depends(deps.check_admin_role),  # Only Admin can create
) -> PositionResponse:
    """
    Create new position (Admin only)
    """
    # Check if position with same name and department already exists
    existing = crud_position.get_position_by_name_and_department(
        db, name=position.name, department_id=position.department_id
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Position with this name already exists in the specified department"
        )
    
    db_position = crud_position.create_position(db=db, position=position)
    return crud_position.get_position_with_counts(db, db_position.id)


@router.get("/{position_id}", response_model=PositionResponse)
def read_position(
    position_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> PositionResponse:
    """
    Get a specific position by ID
    """
    position = crud_position.get_position_with_counts(db, position_id=position_id)
    if not position:
        raise HTTPException(
            status_code=404,
            detail="Position not found"
        )
    
    return position


@router.put("/{position_id}", response_model=PositionResponse)
def update_position(
    *,
    db: Session = Depends(deps.get_db),
    position_id: int,
    position_update: PositionUpdate,
    current_user: User = Depends(deps.check_admin_role),  # Only Admin can update
) -> PositionResponse:
    """
    Update a position by ID (Admin only)
    """
    position = crud_position.get_position(db, position_id=position_id)
    if not position:
        raise HTTPException(
            status_code=404,
            detail="Position not found"
        )
    
    # Check name uniqueness if updating name
    if position_update.name and (
        position_update.name != position.name or
        (position_update.department_id is not None and position_update.department_id != position.department_id)
    ):
        dept_id = position_update.department_id if position_update.department_id is not None else position.department_id
        existing_position = crud_position.get_position_by_name_and_department(
            db, name=position_update.name, department_id=dept_id
        )
        if existing_position and existing_position.id != position_id:
            raise HTTPException(
                status_code=400,
                detail="Position with this name already exists in the specified department"
            )
    
    updated_position = crud_position.update_position(
        db=db, position_id=position_id, position_update=position_update
    )
    
    return crud_position.get_position_with_counts(db, updated_position.id)


@router.delete("/{position_id}")
def delete_position(
    *,
    db: Session = Depends(deps.get_db),
    position_id: int,
    current_user: User = Depends(deps.check_admin_role),  # Only Admin can delete
) -> dict:
    """
    Delete a position by ID (Admin only)
    If position has employees, it will be soft deleted (marked as inactive)
    """
    position = crud_position.get_position(db, position_id=position_id)
    if not position:
        raise HTTPException(
            status_code=404,
            detail="Position not found"
        )
    
    success = crud_position.delete_position(db, position_id=position_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete position"
        )
    
    return {
        "message": "Position deleted successfully",
        "deleted": True,
        "position_id": position_id
    }
