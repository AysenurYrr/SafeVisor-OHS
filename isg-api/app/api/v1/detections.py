"""
Detection API endpoints for PPE detection system integration.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query, Header
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import os
import logging

from app.api import deps
from app.models.user import User
from app.services.detector_service import detector_service
from app.schemas.detection import DetectionResponse, ViolationResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/run/{camera_id}")
def start_detection(
    camera_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> Dict[str, Any]:
    """
    Start PPE detection on the specified camera stream.
    This endpoint initiates detection but doesn't stream video.
    """
    # Validate camera_id (currently supports 1, 2, 3 for demo videos)
    if camera_id not in [1, 2, 3]:
        raise HTTPException(
            status_code=404,
            detail="Camera not found. Supported cameras: 1, 2, 3"
        )
    
    # Check if detector service is available
    if not detector_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="PPE detection service is not available. Please check if the AI model is loaded."
        )
    
    # Map camera_id to video file
    camera_video_mapping = {
        1: "demo.mp4",
        2: "demo2.mp4", 
        3: "demo3.mp4"
    }
    
    video_filename = camera_video_mapping[camera_id]
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # .../app
    video_path = os.path.join(base_dir, "static", "videos", video_filename)
    
    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=404,
            detail=f"Video file not found for camera {camera_id}: {video_filename}"
        )
    
    return {
        "message": f"PPE detection started for Camera-{camera_id}",
        "camera_id": camera_id,
        "video_file": video_filename,
        "status": "running",
        "stream_url": f"/api/v1/detections/stream/{camera_id}"
    }


@router.get("/stream/{camera_id}")
def stream_detection(
    camera_id: int,
    db: Session = Depends(deps.get_db),
    token_header: Optional[HTTPAuthorizationCredentials] = Depends(deps.security_scheme),
    token_q: Optional[str] = Query(default=None, alias="token"),
    token_alt: Optional[str] = Query(default=None, alias="access_token"),
):
    """
    Stream video frames with PPE detection overlays for the specified camera.
    Returns an MJPEG stream suitable for display in web browsers.
    """
    # Authenticate (accept Authorization header or token query param)
    from app.core import security as _security
    from app.crud import user as _crud_user

    token_value: Optional[str] = None
    if token_header and getattr(token_header, "credentials", None):
        token_value = token_header.credentials
    elif token_q:
        token_value = token_q
    elif token_alt:
        token_value = token_alt

    if not token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")

    try:
        tok = token_value.strip().strip('"').strip("'")
        if tok.lower().startswith("bearer "):
            tok = tok[7:].strip()
        payload = _security.verify_token(tok)
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

    # Validate camera_id
    if camera_id not in [1, 2, 3]:
        raise HTTPException(
            status_code=404,
            detail="Camera not found. Supported cameras: 1, 2, 3"
        )
    
    # Check if detector service is available
    if not detector_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="PPE detection service is not available. Please check if the AI model is loaded."
        )
    
    # Map camera_id to base video name and resolve existing extension
    base_names = {1: "demo", 2: "demo2", 3: "demo3"}
    video_basename = base_names[camera_id]
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # .../app
    videos_dir = os.path.join(base_dir, "static", "videos")

    candidates = [
        f"{video_basename}.mp4",
        f"{video_basename}.m4v",
        f"{video_basename}.m4",
        f"{video_basename}.webm",
        f"{video_basename}.mov",
    ]
    video_path: Optional[str] = None
    for name in candidates:
        p = os.path.join(videos_dir, name)
        if os.path.exists(p):
            video_path = p
            break

    if not video_path:
        raise HTTPException(
            status_code=404,
            detail=f"Video file not found for camera {camera_id}. Place one of these under app/static/videos/: {', '.join(candidates)}"
        )
    
    def generate_stream():
        """Generate MJPEG stream with detection overlays."""
        try:
            for frame_bytes in detector_service.process_video_stream(video_path, camera_id=camera_id, db_session=db):
                header = (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n'
                    + f"Content-Length: {len(frame_bytes)}\r\n\r\n".encode('ascii')
                )
                yield header + frame_bytes + b'\r\n'
        except Exception as e:
            logger.error(f"Error generating detection stream: {e}")
            yield b'--frame\r\n'
    
    return StreamingResponse(
        generate_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )


@router.get("/reports", response_model=List[ViolationResponse])
def get_violation_reports(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    limit: int = 100,
    skip: int = 0,
    camera_id: Optional[int] = Query(default=None, description="Filter by camera id"),
) -> List[ViolationResponse]:
    """
    Get PPE violation reports from database.
    """
    from app.crud.violation import get_violations
    from app.schemas.violation import ViolationResponse as DBViolationResponse
    import json
    
    # Get violations from database
    violations = get_violations(db=db, skip=skip, limit=limit, camera_id=camera_id)
    
    # Convert to the API response format
    response_violations = []
    for violation in violations:
        # Parse bbox coordinates if available
        bbox_data = None
        if violation.bbox_coordinates:
            try:
                bbox_data = json.loads(violation.bbox_coordinates)
            except (json.JSONDecodeError, ValueError):
                bbox_data = None
        
        response_violation = ViolationResponse(
            id=violation.id,
            camera_id=violation.camera_id,
            violation_type=str(getattr(violation.violation_type, "value", violation.violation_type)),
            description=violation.description or "",
            timestamp=violation.created_at.isoformat(),
            confidence=(violation.confidence_score or 0) / 100.0,  # Convert back to 0-1 range
            employee_id=str(violation.employee_id) if violation.employee_id is not None else None,
            resolved=(str(getattr(violation.status, "value", violation.status)) == "resolved"),
            bbox_coordinates=bbox_data  # Include bounding box data
        )
        response_violations.append(response_violation)
    
    return response_violations


@router.get("/status")
def get_detection_status() -> Dict[str, Any]:
    """
    Get the status of the PPE detection service.
    """
    return {
        "service_available": detector_service.is_available(),
        "model_loaded": detector_service._model_loaded if hasattr(detector_service, '_model_loaded') else False,
        "supported_cameras": [1, 2, 3],
        "detection_classes": ["helmet", "vest", "face", "person"]
    }