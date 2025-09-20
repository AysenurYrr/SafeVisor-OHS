from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import camera as crud_camera
from app.models.user import User
from app.schemas.camera import (
    CameraCreate, 
    CameraUpdate, 
    CameraResponse,
    CameraListResponse,
    CameraStatus
)

router = APIRouter()


@router.get("/", response_model=CameraListResponse)
def read_cameras(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    location: Optional[str] = Query(None),
    camera_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_recording: Optional[bool] = Query(None),
    detection_enabled: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> CameraListResponse:
    """
    Retrieve cameras with optional filters
    """
    cameras = crud_camera.get_cameras(
        db=db,
        skip=skip,
        limit=limit,
        location=location,
        camera_type=camera_type,
        is_active=is_active,
        is_recording=is_recording,
        detection_enabled=detection_enabled,
        search=search
    )
    
    total = crud_camera.count_cameras(
        db=db,
        location=location,
        camera_type=camera_type,
        is_active=is_active,
        is_recording=is_recording,
        detection_enabled=detection_enabled,
        search=search
    )
    
    return CameraListResponse(
        cameras=cameras,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )


@router.post("/", response_model=CameraResponse)
def create_camera(
    *,
    db: Session = Depends(deps.get_db),
    camera_in: CameraCreate,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> CameraResponse:
    """
    Create new camera (Manager/Admin only)
    """
    # Check if camera with name already exists
    camera = crud_camera.get_camera_by_name(db, name=camera_in.name)
    if camera:
        raise HTTPException(
            status_code=400,
            detail="Camera with this name already exists in the system.",
        )
    
    camera = crud_camera.create_camera(
        db=db, camera=camera_in, created_by=current_user.id
    )
    return camera


@router.get("/{camera_id}", response_model=CameraResponse)
def read_camera(
    camera_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> CameraResponse:
    """
    Get a specific camera by ID
    """
    camera = crud_camera.get_camera(db, camera_id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )
    
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(
    *,
    db: Session = Depends(deps.get_db),
    camera_id: int,
    camera_in: CameraUpdate,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> CameraResponse:
    """
    Update a camera (Manager/Admin only)
    """
    camera = crud_camera.get_camera(db, camera_id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )
    
    # Check name uniqueness if updating name
    if camera_in.name and camera_in.name != camera.name:
        existing_camera = crud_camera.get_camera_by_name(db, name=camera_in.name)
        if existing_camera:
            raise HTTPException(
                status_code=400,
                detail="Camera with this name already exists"
            )
    
    camera = crud_camera.update_camera(
        db=db, camera_id=camera_id, camera_update=camera_in
    )
    return camera


@router.delete("/{camera_id}")
def delete_camera(
    *,
    db: Session = Depends(deps.get_db),
    camera_id: int,
    current_user: User = Depends(deps.check_admin_role),
) -> dict:
    """
    Delete a camera (Admin only)
    """
    camera = crud_camera.get_camera(db, camera_id=camera_id)
    if not camera:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )
    
    success = crud_camera.delete_camera(db, camera_id=camera_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete camera"
        )
    
    return {"message": "Camera deleted successfully"}


@router.get("/active/list", response_model=List[CameraResponse])
def get_active_cameras(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[CameraResponse]:
    """
    Get all active cameras
    """
    return crud_camera.get_active_cameras(db)


@router.get("/recording/list", response_model=List[CameraResponse])
def get_recording_cameras(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[CameraResponse]:
    """
    Get all cameras that are currently recording
    """
    return crud_camera.get_recording_cameras(db)


@router.get("/locations/list")
def get_camera_locations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[str]:
    """
    Get all unique camera locations
    """
    return crud_camera.get_camera_locations(db)


@router.post("/{camera_id}/heartbeat")
def camera_heartbeat(
    camera_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Update camera last_seen timestamp (heartbeat)
    """
    success = crud_camera.update_camera_last_seen(db, camera_id=camera_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Camera not found"
        )
    
    return {"message": "Camera heartbeat updated"}