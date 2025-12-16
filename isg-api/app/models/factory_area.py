from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


# Association table for many-to-many relationship between areas and safety rules
area_rules = Table(
    'area_rules',
    Base.metadata,
    Column('area_id', Integer, ForeignKey('factory_areas.id', ondelete='CASCADE'), primary_key=True),
    Column('rule_name', String(50), primary_key=True)
)


class FactoryArea(Base):
    __tablename__ = "factory_areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by_user = relationship("User", back_populates="created_factory_areas", lazy="select")
    cameras = relationship("Camera", back_populates="factory_area", lazy="select", cascade="all")
    violations = relationship("Violation", back_populates="factory_area", lazy="select")
