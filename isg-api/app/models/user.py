from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    profile_image = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    role = relationship("Role", back_populates="users", lazy="select")
    created_employees = relationship("Employee", back_populates="created_by_user", lazy="select")
    created_cameras = relationship("Camera", back_populates="created_by_user", lazy="select")