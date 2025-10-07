from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Union
from datetime import datetime, date
import uuid as uuid_lib


class EmployeeBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    hire_date: date
    birth_date: Optional[date] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    photo_front_path: Optional[str] = None
    photo_left_path: Optional[str] = None
    photo_right_path: Optional[str] = None
    violation_score: int = 0
    is_active: bool = True
    notes: Optional[str] = None
    face_embedding: Optional[list[float]] = None


class EmployeeCreate(EmployeeBase):
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Employee ID must be at least 3 characters long')
        return v


class EmployeeUpdate(BaseModel):
    employee_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    hire_date: Optional[date] = None
    birth_date: Optional[date] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    photo_front_path: Optional[str] = None
    photo_left_path: Optional[str] = None
    photo_right_path: Optional[str] = None
    violation_score: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class EmployeeInDB(EmployeeBase):
    id: int
    uuid: Union[str, uuid_lib.UUID]
    face_embedding: Optional[list[float]] = None
    # Foreign key ids (new schema)
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    # Convenience resolved names (not persisted; populated at response time)
    department_name: Optional[str] = None
    position_name: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeResponse(EmployeeBase):
    id: int
    uuid: Union[str, uuid_lib.UUID]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Computed/presentation fields
    status: Optional[str] = None
    last_activity: Optional[str] = None
    face_embedding: Optional[list[float]] = None
    # Foreign key ids
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    # Resolved names (derived from relationships)
    department_name: Optional[str] = None
    position_name: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    employees: list[EmployeeResponse]
    total: int
    page: int
    per_page: int