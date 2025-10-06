from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class Employee(Base):
    __tablename__ = "employees"
    # Keep existing integer PK for backward compatibility; adding UUID column for new API spec
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(PG_UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, server_default=func.gen_random_uuid())
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)
    hire_date = Column(Date, nullable=False)
    birth_date = Column(Date, nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    emergency_phone = Column(String(20), nullable=True)
    photo_url = Column(String(500), nullable=True)
    # Three required profile photos
    photo_front_path = Column(String(500), nullable=True)
    photo_left_path = Column(String(500), nullable=True)
    photo_right_path = Column(String(500), nullable=True)
    face_encoding = Column(Text, nullable=True)  # JSON string for face recognition
    violation_score = Column(Integer, default=0, nullable=False)  # Track violation count/score
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by_user = relationship("User", back_populates="created_employees", lazy="select")
    violations = relationship("Violation", back_populates="employee", lazy="select")
    pose_alerts = relationship("PoseAlert", back_populates="employee", lazy="select")
    photos = relationship("EmployeePhoto", back_populates="employee", cascade="all, delete-orphan", lazy="select")


class EmployeePhoto(Base):
    __tablename__ = "employee_photos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)

    employee = relationship("Employee", back_populates="photos")