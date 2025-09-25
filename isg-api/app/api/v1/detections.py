"""
Detection API endpoints for PPE detection system integration.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
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
    current_user: User = Depends(deps.check_manager_or_admin_role),
):
    """
    Stream video frames with PPE detection overlays for the specified camera.
    Returns an MJPEG stream suitable for display in web browsers.
    """
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
    
    def generate_stream():
        """Generate MJPEG stream with detection overlays."""
        try:
            for frame_bytes in detector_service.process_video_stream(video_path, camera_id=camera_id, db_session=db):
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
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
) -> List[ViolationResponse]:
    """
    Get PPE violation reports from database.
    """
    from app.crud.violation import get_violations
    from app.schemas.violation import ViolationResponse as DBViolationResponse
    import json
    
    # Get violations from database
    violations = get_violations(db=db, skip=skip, limit=limit)
    
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
            violation_type=violation.violation_type.value,
            description=violation.description or "",
            timestamp=violation.created_at.isoformat(),
            confidence=violation.confidence_score / 100.0,  # Convert back to 0-1 range
            employee_id=violation.employee_id,
            resolved=(violation.status.value == "resolved"),
            bbox_coordinates=bbox_data  # Include bounding box data
        )
        response_violations.append(response_violation)
    
    return response_violations


@router.get("/status")
def get_detection_status(
    current_user: User = Depends(deps.get_current_active_user),
) -> Dict[str, Any]:
    """
    Get the status of the PPE detection service.
    """
    return {
        "service_available": detector_service.is_available(),
        "model_loaded": detector_service._model_loaded if hasattr(detector_service, '_model_loaded') else False,
        "supported_cameras": [1, 2, 3],
        "detection_classes": ["helmet", "vest", "face", "person"]
    }