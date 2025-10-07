from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Department name cannot be empty')
        return v.strip()


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Department name cannot be empty')
        return v.strip() if v else v


class DepartmentInDB(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DepartmentResponse(DepartmentInDB):
    employee_count: Optional[int] = 0
    position_count: Optional[int] = 0

    class Config:
        from_attributes = True
