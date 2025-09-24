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
            for frame_bytes in detector_service.process_video_stream(video_path):
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
    Get PPE violation reports.
    
    Note: This is a placeholder implementation. In a real system, 
    violations would be stored in the database and retrieved here.
    """
    # TODO: Implement database storage and retrieval of violations
    # For now, return sample data to demonstrate the API structure
    
    sample_violations = [
        {
            "id": 1,
            "camera_id": 1,
            "violation_type": "no_helmet",
            "description": "Person without safety helmet detected",
            "timestamp": "2024-01-20T10:30:00Z",
            "confidence": 0.85,
            "employee_id": None,
            "resolved": False
        },
        {
            "id": 2,
            "camera_id": 2,
            "violation_type": "no_vest",
            "description": "Person without safety vest detected", 
            "timestamp": "2024-01-20T11:15:00Z",
            "confidence": 0.92,
            "employee_id": None,
            "resolved": False
        },
        {
            "id": 3,
            "camera_id": 1,
            "violation_type": "no_helmet",
            "description": "Person without safety helmet detected",
            "timestamp": "2024-01-20T12:00:00Z",
            "confidence": 0.78,
            "employee_id": None,
            "resolved": True
        }
    ]
    
    # Apply pagination
    end_idx = skip + limit
    paginated_violations = sample_violations[skip:end_idx]
    
    return [ViolationResponse(**violation) for violation in paginated_violations]


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