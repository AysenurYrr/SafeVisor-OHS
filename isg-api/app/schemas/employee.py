from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime, date


class EmployeeBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: str
    position: str
    hire_date: date
    birth_date: Optional[date] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    face_encoding: Optional[str] = None
    
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
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[date] = None
    birth_date: Optional[date] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    photo_url: Optional[str] = None
    face_encoding: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class EmployeeInDB(EmployeeBase):
    id: int
    face_encoding: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeResponse(EmployeeBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    employees: list[EmployeeResponse]
    total: int
    page: int
    per_page: int