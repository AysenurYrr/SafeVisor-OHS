from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import factory_area as crud_factory_area
from app.models.user import User
from app.schemas.factory_area import (
    FactoryAreaCreate,
    FactoryAreaUpdate,
    FactoryAreaResponse,
    FactoryAreaListResponse,
    VALID_SAFETY_RULES
)

router = APIRouter()


@router.get("/safety-rules", response_model=List[str])
def get_valid_safety_rules(
    current_user: User = Depends(deps.get_current_active_user),
) -> List[str]:
    """
    Get list of valid safety rules that can be assigned to factory areas
    """
    return VALID_SAFETY_RULES


@router.get("/", response_model=FactoryAreaListResponse)
def read_factory_areas(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> FactoryAreaListResponse:
    """
    Retrieve factory areas with optional filters
    """
    areas = crud_factory_area.get_factory_areas(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search
    )
    
    # Load safety rules for each area
    for area in areas:
        area.safety_rules = crud_factory_area.get_area_safety_rules(db, area.id)
    
    total = crud_factory_area.count_factory_areas(
        db=db,
        is_active=is_active,
        search=search
    )
    
    return FactoryAreaListResponse(
        areas=areas,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )


@router.post("/", response_model=FactoryAreaResponse)
def create_factory_area(
    *,
    db: Session = Depends(deps.get_db),
    area_in: FactoryAreaCreate,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> FactoryAreaResponse:
    """
    Create new factory area (Manager/Admin only)
    """
    # Check if area with name already exists
    area = crud_factory_area.get_factory_area_by_name(db, name=area_in.name)
    if area:
        raise HTTPException(
            status_code=400,
            detail="Factory area with this name already exists in the system.",
        )
    
    area = crud_factory_area.create_factory_area(
        db=db, area=area_in, created_by=current_user.id
    )
    
    # Load safety rules
    area.safety_rules = crud_factory_area.get_area_safety_rules(db, area.id)
    
    return area


@router.get("/{area_id}", response_model=FactoryAreaResponse)
def read_factory_area(
    area_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> FactoryAreaResponse:
    """
    Get a specific factory area by ID
    """
    area = crud_factory_area.get_factory_area(db, area_id=area_id)
    if not area:
        raise HTTPException(
            status_code=404,
            detail="Factory area not found"
        )
    
    # Load safety rules
    area.safety_rules = crud_factory_area.get_area_safety_rules(db, area.id)
    
    return area


@router.put("/{area_id}", response_model=FactoryAreaResponse)
def update_factory_area(
    *,
    db: Session = Depends(deps.get_db),
    area_id: int,
    area_in: FactoryAreaUpdate,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> FactoryAreaResponse:
    """
    Update a factory area (Manager/Admin only)
    """
    area = crud_factory_area.get_factory_area(db, area_id=area_id)
    if not area:
        raise HTTPException(
            status_code=404,
            detail="Factory area not found"
        )
    
    # Check name uniqueness if updating name
    if area_in.name and area_in.name != area.name:
        existing_area = crud_factory_area.get_factory_area_by_name(db, name=area_in.name)
        if existing_area:
            raise HTTPException(
                status_code=400,
                detail="Factory area with this name already exists"
            )
    
    area = crud_factory_area.update_factory_area(
        db=db, area_id=area_id, area_update=area_in
    )
    
    # Load safety rules
    area.safety_rules = crud_factory_area.get_area_safety_rules(db, area.id)
    
    return area


@router.delete("/{area_id}")
def delete_factory_area(
    *,
    db: Session = Depends(deps.get_db),
    area_id: int,
    current_user: User = Depends(deps.check_admin_role),
) -> dict:
    """
    Delete a factory area (Admin only)
    """
    area = crud_factory_area.get_factory_area(db, area_id=area_id)
    if not area:
        raise HTTPException(
            status_code=404,
            detail="Factory area not found"
        )
    
    success = crud_factory_area.delete_factory_area(db, area_id=area_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete factory area"
        )
    
    return {"message": "Factory area deleted successfully"}


@router.get("/active/list", response_model=List[FactoryAreaResponse])
def get_active_factory_areas(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[FactoryAreaResponse]:
    """
    Get all active factory areas
    """
    areas = crud_factory_area.get_active_factory_areas(db)
    
    # Load safety rules for each area
    for area in areas:
        area.safety_rules = crud_factory_area.get_area_safety_rules(db, area.id)
    
    return areas
