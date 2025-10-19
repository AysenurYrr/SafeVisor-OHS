from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.session import Base


class ViolationType(enum.Enum):
    NO_HELMET = "no_helmet"
    NO_VEST = "no_vest"
    NO_GLOVES = "no_gloves"
    NO_BOOTS = "no_boots"
    NO_MASK = "no_mask"
    NO_GOGGLES = "no_goggles"
    INCOMPLETE_PPE = "incomplete_ppe"


class ViolationSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationStatus(enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    violation_type = Column(Enum(ViolationType), nullable=False)
    severity = Column(Enum(ViolationSeverity), default=ViolationSeverity.MEDIUM)
    status = Column(Enum(ViolationStatus), default=ViolationStatus.OPEN)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    confidence_score = Column(Integer, nullable=False, default=0)  # 0-100
    bbox_coordinates = Column(Text, nullable=True)  # JSON string
    
    # Evidence images (start, middle, end frames)
    evidence_start_image = Column(String(500), nullable=True)
    evidence_middle_image = Column(String(500), nullable=True)
    evidence_end_image = Column(String(500), nullable=True)
    
    # Additional tracking fields
    person_tracker_id = Column(Integer, nullable=True)  # Temporal tracker ID
    duration_frames = Column(Integer, nullable=True)  # How many frames violation lasted
    
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="violations", lazy="select")
    camera = relationship("Camera", back_populates="violations", lazy="select")