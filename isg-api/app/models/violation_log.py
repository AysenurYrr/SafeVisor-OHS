from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.dialects.postgresql import JSONB


class ViolationLog(Base):
    __tablename__ = "violation_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    violation_types = Column(JSONB, nullable=False)  # Array of strings
    image_paths = Column(JSONB, nullable=True)  # Array of strings
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    duration = Column(Float, nullable=True)  # Duration in seconds
    reported = Column(Boolean, default=False, nullable=False)
    bounding_boxes = Column(JSONB, nullable=True)  # Optional bounding box data
    
    # Relationships
    employee = relationship("Employee", back_populates="violation_logs", lazy="select")
    camera = relationship("Camera", back_populates="violation_logs", lazy="select")

    # Add indexes for performance
    __table_args__ = (
        Index('ix_violation_logs_timestamp', 'timestamp'),
        Index('ix_violation_logs_employee_timestamp', 'employee_id', 'timestamp'),
        Index('ix_violation_logs_camera_timestamp', 'camera_id', 'timestamp'),
        Index('ix_violation_logs_reported', 'reported'),
    )