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
    # Check if area with name already exists (including inactive/soft-deleted)
    existing = crud_factory_area.get_factory_area_by_name(db, name=area_in.name)
    if existing:
        if existing.is_active:
            # Active duplicate
            raise HTTPException(
                status_code=400,
                detail="Factory area with this name already exists in the system.",
            )
        # Reactivate previously soft-deleted area (treat as upsert)
        update_payload = FactoryAreaUpdate(
            name=area_in.name,
            description=area_in.description,
            is_active=True,
            camera_ids=area_in.camera_ids,
            safety_rules=area_in.safety_rules
        )
        reactivated = crud_factory_area.update_factory_area(
            db=db, area_id=existing.id, area_update=update_payload
        )
        # Ensure rules loaded
        reactivated.safety_rules = crud_factory_area.get_area_safety_rules(db, existing.id)
        return reactivated

    # Create brand new area
    area = crud_factory_area.create_factory_area(
        db=db, area=area_in, created_by=current_user.id
    )
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
    Permanently delete a factory area (Admin only)
    """
    area = crud_factory_area.get_factory_area(db, area_id=area_id)
    if not area:
        raise HTTPException(
            status_code=404,
            detail="Factory area not found"
        )
    # Perform hard delete
    success = crud_factory_area.hard_delete_factory_area(db, area_id=area_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete factory area"
        )
    return {"message": "Factory area permanently deleted"}


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


@router.post("/{area_id}/cameras/{camera_id}/link")
def link_camera_to_area(
    *,
    db: Session = Depends(deps.get_db),
    area_id: int,
    camera_id: int,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> dict:
    """
    Link a camera to a factory area (Manager/Admin only)
    """
    from app.models.camera import Camera
    
    area = crud_factory_area.get_factory_area(db, area_id=area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Factory area not found")
    
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Check if camera is already linked to another area
    if camera.factory_area_id is not None and camera.factory_area_id != area_id:
        raise HTTPException(
            status_code=400,
            detail=f"Camera '{camera.name}' is already linked to another factory area"
        )
    
    camera.factory_area_id = area_id
    db.commit()
    
    return {"message": f"Camera '{camera.name}' linked to factory area '{area.name}'"}


@router.delete("/{area_id}/cameras/{camera_id}/unlink")
def unlink_camera_from_area(
    *,
    db: Session = Depends(deps.get_db),
    area_id: int,
    camera_id: int,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> dict:
    """
    Unlink a camera from a factory area (Manager/Admin only)
    """
    from app.models.camera import Camera
    
    area = crud_factory_area.get_factory_area(db, area_id=area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Factory area not found")
    
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if camera.factory_area_id != area_id:
        raise HTTPException(
            status_code=400,
            detail=f"Camera '{camera.name}' is not linked to this factory area"
        )
    
    camera.factory_area_id = None
    db.commit()
    
    return {"message": f"Camera '{camera.name}' unlinked from factory area '{area.name}'"}


@router.get("/{area_id}/available-cameras")
def get_available_cameras(
    *,
    db: Session = Depends(deps.get_db),
    area_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> List[dict]:
    """
    Get list of cameras that are not linked to any factory area (available for linking)
    """
    from app.models.camera import Camera
    
    area = crud_factory_area.get_factory_area(db, area_id=area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Factory area not found")
    
    # Get all cameras that are not linked to any area
    available_cameras = db.query(Camera).filter(Camera.factory_area_id == None).all()
    
    return [
        {
            "id": cam.id,
            "name": cam.name,
            "location": cam.location,
            "stream_url": cam.stream_url,
            "is_active": cam.is_active,
            "camera_type": cam.camera_type,
        }
        for cam in available_cameras
    ]

