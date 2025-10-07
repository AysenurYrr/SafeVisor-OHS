from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EmployeeLogBase(BaseModel):
    employee_id: int
    action: str  # 'created', 'updated', 'deleted'
    actor_id: Optional[int] = None
    details: Optional[dict] = None


class EmployeeLogCreate(EmployeeLogBase):
    pass


class EmployeeLogInDB(EmployeeLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class EmployeeLogResponse(EmployeeLogInDB):
    actor_name: Optional[str] = None
    employee_name: Optional[str] = None

    class Config:
        from_attributes = True
