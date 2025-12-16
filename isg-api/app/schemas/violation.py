from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ViolationTypeEnum(str, Enum):
    NO_HELMET = "no_helmet"
    NO_VEST = "no_vest"
    NO_GLOVES = "no_gloves"
    NO_BOOTS = "no_boots"
    NO_MASK = "no_mask"
    NO_GOGGLES = "no_goggles"
    INCOMPLETE_PPE = "incomplete_ppe"


class ViolationSeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationStatusEnum(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class ViolationBase(BaseModel):
    employee_id: Optional[int] = None
    camera_id: int
    factory_area_id: Optional[int] = None
    violation_type: ViolationTypeEnum
    severity: ViolationSeverityEnum = ViolationSeverityEnum.MEDIUM
    status: ViolationStatusEnum = ViolationStatusEnum.OPEN
    description: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    confidence_score: int = 0
    bbox_coordinates: Optional[str] = None
    occurred_at: Optional[datetime] = None
    
    # Evidence images
    evidence_start_image: Optional[str] = None
    evidence_middle_image: Optional[str] = None
    evidence_end_image: Optional[str] = None
    
    # Tracking fields
    person_tracker_id: Optional[int] = None
    duration_frames: Optional[int] = None


class ViolationCreate(ViolationBase):
    pass


class ViolationUpdate(BaseModel):
    status: Optional[ViolationStatusEnum] = None
    severity: Optional[ViolationSeverityEnum] = None
    description: Optional[str] = None
    resolution_notes: Optional[str] = None


class ViolationInDB(ViolationBase):
    id: int
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    notification_sent: bool = False
    occurred_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Evidence images
    evidence_start_image: Optional[str] = None
    evidence_middle_image: Optional[str] = None
    evidence_end_image: Optional[str] = None
    
    # Tracking fields
    person_tracker_id: Optional[int] = None
    duration_frames: Optional[int] = None

    class Config:
        from_attributes = True


class ViolationResponse(ViolationBase):
    id: int
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    notification_sent: bool = False
    occurred_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Evidence images
    evidence_start_image: Optional[str] = None
    evidence_middle_image: Optional[str] = None
    evidence_end_image: Optional[str] = None
    
    # Tracking fields
    person_tracker_id: Optional[int] = None
    duration_frames: Optional[int] = None

    class Config:
        from_attributes = True


class ViolationListResponse(BaseModel):
    violations: list[ViolationResponse]
    total: int
    page: int
    per_page: int


class ViolationStats(BaseModel):
    total_violations: int
    open_violations: int
    resolved_violations: int
    by_type: dict[str, int]
    by_severity: dict[str, int]