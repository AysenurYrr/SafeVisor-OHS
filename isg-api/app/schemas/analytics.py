from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class AnalyticsBase(BaseModel):
    employee_id: int
    violation_type: str
    violation_date: date
    violation_image_path: Optional[str] = None


class AnalyticsCreate(AnalyticsBase):
    pass


class AnalyticsUpdate(BaseModel):
    employee_id: Optional[int] = None
    violation_type: Optional[str] = None
    violation_date: Optional[date] = None
    violation_image_path: Optional[str] = None


class AnalyticsInDB(AnalyticsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsResponse(AnalyticsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsListResponse(BaseModel):
    analytics: List[AnalyticsResponse]
    total: int
    page: int
    per_page: int


class AnalyticsGenerateRequest(BaseModel):
    date: Optional[date] = None  # Default to today if not provided


class AnalyticsReportsFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    employee_id: Optional[int] = None
    violation_type: Optional[str] = None
    page: int = 1
    per_page: int = 50