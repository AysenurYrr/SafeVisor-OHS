"""
Pydantic schemas for PPE detection system.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DetectionResponse(BaseModel):
    """Response model for detection results."""
    cls_name: str = Field(..., description="Detected class name (helmet, vest, face, person)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    box: List[int] = Field(..., description="Bounding box coordinates [x1, y1, x2, y2]")
    timestamp: datetime = Field(..., description="Detection timestamp")

    class Config:
        from_attributes = True


class ViolationResponse(BaseModel):
    """Response model for PPE violations."""
    id: int = Field(..., description="Violation ID")
    camera_id: int = Field(..., description="Camera ID where violation occurred")
    violation_type: str = Field(..., description="Type of violation (no_helmet, no_vest, etc.)")
    rule_type: str | None = Field(None, description="Configured rule that was violated")
    description: str = Field(..., description="Human-readable description of the violation")
    timestamp: str = Field(..., description="ISO timestamp when violation occurred")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    employee_id: Optional[str] = Field(None, description="Employee ID if identified")
    resolved: bool = Field(False, description="Whether the violation has been resolved")
    bbox_coordinates: Optional[Dict[str, int]] = Field(None, description="Bounding box coordinates {x, y, width, height}")
    snapshot_url: Optional[str] = Field(None, description="URL for stored evidence snapshot")
    track_id: Optional[int] = Field(None, description="Tracking identifier if available")
    model_confidence: Optional[float] = Field(None, description="Raw model confidence reported by detector")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the violation")

    class Config:
        from_attributes = True


class DetectionStartRequest(BaseModel):
    """Request model for starting detection."""
    camera_id: int = Field(..., description="Camera ID to start detection on")
    settings: Optional[Dict[str, Any]] = Field(None, description="Optional detection settings")


class DetectionStatusResponse(BaseModel):
    """Response model for detection service status."""
    service_available: bool = Field(..., description="Whether the detection service is available")
    model_loaded: bool = Field(..., description="Whether the AI model is loaded")
    supported_cameras: List[int] = Field(..., description="List of supported camera IDs")
    detection_classes: List[str] = Field(..., description="List of classes the model can detect")

    # Pydantic v2 config: allow protected namespaces and enable from_attributes
    model_config: ConfigDict = ConfigDict(
        protected_namespaces=(),
        from_attributes=True,
    )
