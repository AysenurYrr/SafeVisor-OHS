from typing import List, Optional, Iterator
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
import os
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


@router.get("/demo")
def stream_demo_video(
    request: Request,
    range: Optional[str] = Header(default=None, alias="Range"),
    token_header: Optional[HTTPAuthorizationCredentials] = Depends(deps.security_scheme),
    token_q: Optional[str] = Query(default=None, alias="token"),
    db: Session = Depends(deps.get_db),
):
    """
    Stream demo video (mp4) with optional HTTP Range support.
    Access restricted to Admin or Manager.
    """
    # Authenticate: Accept Authorization: Bearer ... or token query param
    from app.core import security as _security
    from app.crud import user as _crud_user

    token_value: Optional[str] = None
    if token_header and getattr(token_header, "credentials", None):
        token_value = token_header.credentials
    elif token_q:
        token_value = token_q

    if not token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")

    try:
        payload = _security.verify_token(token_value)
        if payload is None:
            raise ValueError("Invalid token")
        user_id = int(payload)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    user = _crud_user.get_user(db, user_id=user_id)
    if not user or not _crud_user.is_active(user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    # Role check: allow ADMIN or MANAGER or superuser
    names = set()
    if getattr(user, "role", None) and getattr(user.role, "name", None):
        names.add(user.role.name.upper())
    if getattr(user, "roles", None):
        for r in user.roles:
            if r and getattr(r, "name", None):
                names.add(r.name.upper())
    allowed_roles = {"ADMIN", "MANAGER"}
    if not (names & allowed_roles) and not _crud_user.is_superuser(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager or Admin access required")

    # Resolve demo file path: app/static/videos/demo.* (prefer mp4)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # .../app
    videos_dir = os.path.join(base_dir, "static", "videos")
    candidate_names = [
        ("demo.mp4", "video/mp4"),
        ("demo.m4v", "video/mp4"),
        ("demo.m4", "video/mp4"),
        ("demo.webm", "video/webm"),
        ("demo.mov", "video/quicktime"),
    ]
    video_path = None
    content_type = None
    for name, ctype in candidate_names:
        path = os.path.join(videos_dir, name)
        if os.path.exists(path):
            video_path = path
            content_type = ctype
            break

    if not video_path:
        raise HTTPException(status_code=404, detail="Demo video not found. Place demo.mp4 (or demo.m4v/webm/mov) under app/static/videos/")

    file_size = os.path.getsize(video_path)
    chunk_size = 1024 * 1024  # 1MB

    def file_iterator(start: int, end: int):
        with open(video_path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                read_size = min(chunk_size, remaining)
                data = f.read(read_size)
                if not data:
                    break
                remaining -= len(data)
                yield data

    if range is not None:
        # Example Range header: "bytes=0-1023" or "bytes=1024-"
        try:
            bytes_unit, ranges = range.strip().split("=")
            if bytes_unit != "bytes":
                raise ValueError("Only 'bytes' range unit is supported")
            start_str, end_str = ranges.split("-")
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
            # Clamp values
            start = max(0, start)
            end = min(end, file_size - 1)
            if start > end:
                raise ValueError("Invalid Range header")
        except Exception:
            # 416 Range Not Satisfiable
            return StreamingResponse(
                iter(()),
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                headers={
                    "Content-Range": f"bytes */{file_size}",
                    "Accept-Ranges": "bytes",
                },
                media_type=content_type,
            )

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
            "Cache-Control": "no-cache",
        }
        return StreamingResponse(
            file_iterator(start, end),
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            media_type=content_type,
            headers=headers,
        )

    # No Range header: stream full file
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Cache-Control": "no-cache",
    }
    return StreamingResponse(
        file_iterator(0, file_size - 1),
        media_type=content_type,
        headers=headers,
    )

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


@router.get("/{camera_id}/stream")
def stream_camera_video(
    camera_id: int,
    request: Request,
    range: Optional[str] = Header(default=None, alias="Range"),
    token_header: Optional[HTTPAuthorizationCredentials] = Depends(deps.security_scheme),
    token_q: Optional[str] = Query(default=None, alias="token"),
    db: Session = Depends(deps.get_db),
):
    """
    Stream specified demo camera video by camera_id with HTTP Range support.
    Camera-1 -> demo.mp4, Camera-2 -> demo2.mp4, Camera-3 -> demo3.mp4
    Access restricted to Admin or Manager.
    """
    # Authenticate
    from app.core import security as _security
    from app.crud import user as _crud_user

    token_value: Optional[str] = None
    if token_header and getattr(token_header, "credentials", None):
        token_value = token_header.credentials
    elif token_q:
        token_value = token_q
    if not token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
    try:
        payload = _security.verify_token(token_value)
        if payload is None:
            raise ValueError("Invalid token")
        user_id = int(payload)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    user = _crud_user.get_user(db, user_id=user_id)
    if not user or not _crud_user.is_active(user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    # Role check
    names = set()
    if getattr(user, "role", None) and getattr(user.role, "name", None):
        names.add(user.role.name.upper())
    if getattr(user, "roles", None):
        for r in user.roles:
            if r and getattr(r, "name", None):
                names.add(r.name.upper())
    allowed_roles = {"ADMIN", "MANAGER"}
    if not (names & allowed_roles) and not _crud_user.is_superuser(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager or Admin access required")

    # Map camera_id to file name
    mapping = {
        1: ("demo.mp4", "video/mp4"),
        2: ("demo2.mp4", "video/mp4"),
        3: ("demo3.mp4", "video/mp4"),
    }
    if camera_id not in mapping:
        raise HTTPException(status_code=404, detail="Unknown camera id")

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # .../app
    videos_dir = os.path.join(base_dir, "static", "videos")
    filename, content_type = mapping[camera_id]
    video_path = os.path.join(videos_dir, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail=f"Video for camera {camera_id} not found: {filename}")

    file_size = os.path.getsize(video_path)
    chunk_size = 1024 * 1024

    def file_iterator(start: int, end: int):
        with open(video_path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                read_size = min(chunk_size, remaining)
                data = f.read(read_size)
                if not data:
                    break
                remaining -= len(data)
                yield data

    if range is not None:
        try:
            bytes_unit, ranges = range.strip().split("=")
            if bytes_unit != "bytes":
                raise ValueError("Only 'bytes' range unit is supported")
            start_str, end_str = ranges.split("-")
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
            start = max(0, start)
            end = min(end, file_size - 1)
            if start > end:
                raise ValueError("Invalid Range header")
        except Exception:
            return StreamingResponse(
                iter(()),
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                headers={
                    "Content-Range": f"bytes */{file_size}",
                    "Accept-Ranges": "bytes",
                },
                media_type=content_type,
            )

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
            "Cache-Control": "no-cache",
        }
        return StreamingResponse(
            file_iterator(start, end),
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            media_type=content_type,
            headers=headers,
        )

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Cache-Control": "no-cache",
    }
    return StreamingResponse(
        file_iterator(0, file_size - 1),
        media_type=content_type,
        headers=headers,
    )

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


