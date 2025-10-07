from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class PositionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    department_id: Optional[int] = None
    is_active: bool = True


class PositionCreate(PositionBase):
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Position name cannot be empty')
        return v.strip()


class PositionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Position name cannot be empty')
        return v.strip() if v else v


class PositionInDB(PositionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PositionResponse(PositionInDB):
    department_name: Optional[str] = None
    employee_count: Optional[int] = 0

    class Config:
        from_attributes = True
