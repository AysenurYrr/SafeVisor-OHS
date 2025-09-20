from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
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
    face_encoding = Column(Text, nullable=True)  # JSON string for face recognition
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by_user = relationship("User", back_populates="created_employees", lazy="select")
    violations = relationship("Violation", back_populates="employee", lazy="select")
    pose_alerts = relationship("PoseAlert", back_populates="employee", lazy="select")