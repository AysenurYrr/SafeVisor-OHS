from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    violation_type = Column(String(100), nullable=False, index=True)
    violation_date = Column(Date, nullable=False)
    violation_image_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="analytics", lazy="select")

    # Add indexes for performance
    __table_args__ = (
        Index('ix_analytics_employee_date', 'employee_id', 'violation_date'),
        Index('ix_analytics_violation_type', 'violation_type'),
        Index('ix_analytics_date', 'violation_date'),
        Index('ix_analytics_created_at', 'created_at'),
    )