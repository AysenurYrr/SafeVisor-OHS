from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class EmployeeLog(Base):
    __tablename__ = "employee_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # 'created', 'updated', 'deleted'
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    details = Column(JSONB, nullable=True)  # Store changed fields or additional info
    
    # Relationships
    employee = relationship("Employee", back_populates="logs", lazy="select")
    actor = relationship("User", lazy="select")
