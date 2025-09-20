from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    detection_type = Column(String(50), nullable=False)  # person, ppe, face, etc.
    confidence = Column(Float, nullable=False)
    bbox_x = Column(Float, nullable=False)  # Bounding box coordinates
    bbox_y = Column(Float, nullable=False)
    bbox_width = Column(Float, nullable=False)
    bbox_height = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    # 'metadata' is reserved by SQLAlchemy's Declarative API, so use a different
    # Python attribute name while keeping the DB column name as 'metadata'.
    extra_metadata = Column("metadata", Text, nullable=True)  # JSON string for additional data
    frame_timestamp = Column(DateTime(timezone=True), nullable=False)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    camera = relationship("Camera", back_populates="detections", lazy="select")