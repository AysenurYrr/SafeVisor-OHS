from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.session import Base


class PoseType(enum.Enum):
    UNSAFE_LIFTING = "unsafe_lifting"
    POOR_POSTURE = "poor_posture"
    FALL_RISK = "fall_risk"
    ERGONOMIC_RISK = "ergonomic_risk"
    REPETITIVE_STRAIN = "repetitive_strain"
    FATIGUE_DETECTED = "fatigue_detected"


class AlertSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class PoseAlert(Base):
    __tablename__ = "pose_alerts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    pose_type = Column(Enum(PoseType), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    confidence_score = Column(Float, nullable=False, default=0.0)  # 0.0-1.0
    pose_data = Column(Text, nullable=True)  # JSON string of pose keypoints
    risk_assessment = Column(Text, nullable=True)  # JSON string of risk factors
    duration_seconds = Column(Integer, nullable=True)  # How long the pose was held
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="pose_alerts", lazy="select")
    camera = relationship("Camera", back_populates="pose_alerts", lazy="select")