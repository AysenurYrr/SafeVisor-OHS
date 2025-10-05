from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, Union, List
from datetime import datetime, date
import uuid as uuid_lib


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
    violation_score: float = Field(default=0.0, ge=0, le=100)  # 0-100 validation
    face_embeddings: Optional[List[float]] = None


class EmployeeCreate(EmployeeBase):
    face_encoding: Optional[str] = None
    photo_1_path: Optional[str] = None  # Optional - will be set after file upload
    photo_2_path: Optional[str] = None  # Optional - will be set after file upload
    photo_3_path: Optional[str] = None  # Optional - will be set after file upload
    
    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Employee ID must be at least 3 characters long')
        return v
    
    @field_validator('violation_score')
    @classmethod
    def validate_violation_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Violation score must be between 0 and 100')
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
    violation_score: Optional[float] = Field(None, ge=0, le=100)
    photo_1_path: Optional[str] = None
    photo_2_path: Optional[str] = None
    photo_3_path: Optional[str] = None
    face_embeddings: Optional[List[float]] = None


class EmployeeInDB(EmployeeBase):
    id: int
    uuid: Union[str, uuid_lib.UUID]
    face_encoding: Optional[str] = None
    photo_1_path: Optional[str] = None
    photo_2_path: Optional[str] = None
    photo_3_path: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeResponse(EmployeeBase):
    id: int
    uuid: Union[str, uuid_lib.UUID]
    photo_1_path: Optional[str] = None
    photo_2_path: Optional[str] = None
    photo_3_path: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Computed/presentation fields
    status: Optional[str] = None
    last_activity: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    employees: list[EmployeeResponse]
    total: int
    page: int
    per_page: int