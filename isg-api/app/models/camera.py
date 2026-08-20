from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    port = Column(Integer, default=554)
    stream_url = Column(String(500), nullable=False)
    camera_type = Column(String(50), default="ip")  # ip, usb, etc.
    resolution = Column(String(20), default="1920x1080")
    fps = Column(Integer, default=30)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    is_recording = Column(Boolean, default=False)
    detection_enabled = Column(Boolean, default=True)
    ppe_detection = Column(Boolean, default=True)
    pose_detection = Column(Boolean, default=True)
    face_recognition = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    factory_area_id = Column(Integer, ForeignKey("factory_areas.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by_user = relationship("User", back_populates="created_cameras", lazy="select")
    detections = relationship("Detection", back_populates="camera", lazy="select")
    violations = relationship("Violation", back_populates="camera", lazy="select")
    pose_alerts = relationship("PoseAlert", back_populates="camera", lazy="select")
    factory_area = relationship("FactoryArea", back_populates="cameras", lazy="select")
    safety_rules = relationship("SafetyRule", back_populates="camera", lazy="select", cascade="all, delete-orphan")
