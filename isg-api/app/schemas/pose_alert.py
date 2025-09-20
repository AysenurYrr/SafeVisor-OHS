from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class PoseTypeEnum(str, Enum):
    UNSAFE_LIFTING = "unsafe_lifting"
    POOR_POSTURE = "poor_posture"
    FALL_RISK = "fall_risk"
    ERGONOMIC_RISK = "ergonomic_risk"
    REPETITIVE_STRAIN = "repetitive_strain"
    FATIGUE_DETECTED = "fatigue_detected"


class AlertSeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatusEnum(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class PoseAlertBase(BaseModel):
    employee_id: Optional[int] = None
    camera_id: int
    pose_type: PoseTypeEnum
    severity: AlertSeverityEnum = AlertSeverityEnum.MEDIUM
    status: AlertStatusEnum = AlertStatusEnum.ACTIVE
    description: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    confidence_score: float = 0.0
    pose_data: Optional[str] = None
    risk_assessment: Optional[str] = None
    duration_seconds: Optional[int] = None


class PoseAlertCreate(PoseAlertBase):
    pass


class PoseAlertUpdate(BaseModel):
    status: Optional[AlertStatusEnum] = None
    severity: Optional[AlertSeverityEnum] = None
    description: Optional[str] = None
    resolution_notes: Optional[str] = None


class PoseAlertInDB(PoseAlertBase):
    id: int
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    notification_sent: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PoseAlertResponse(PoseAlertBase):
    id: int
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    notification_sent: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PoseAlertListResponse(BaseModel):
    pose_alerts: list[PoseAlertResponse]
    total: int
    page: int
    per_page: int


class PoseAlertStats(BaseModel):
    total_alerts: int
    active_alerts: int
    resolved_alerts: int
    by_type: dict[str, int]
    by_severity: dict[str, int]