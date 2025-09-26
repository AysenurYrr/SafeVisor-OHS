from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ViolationLogBase(BaseModel):
    employee_id: Optional[int] = None
    camera_id: int
    violation_types: List[str]  # Array of violation type strings
    image_paths: Optional[List[str]] = None  # Array of image paths
    duration: Optional[float] = None  # Duration in seconds
    reported: bool = False
    bounding_boxes: Optional[Any] = None  # JSON data for bounding boxes


class ViolationLogCreate(ViolationLogBase):
    pass


class ViolationLogUpdate(BaseModel):
    employee_id: Optional[int] = None
    camera_id: Optional[int] = None
    violation_types: Optional[List[str]] = None
    image_paths: Optional[List[str]] = None
    duration: Optional[float] = None
    reported: Optional[bool] = None
    bounding_boxes: Optional[Any] = None


class ViolationLogInDB(ViolationLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ViolationLogResponse(ViolationLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ViolationLogListResponse(BaseModel):
    violation_logs: List[ViolationLogResponse]
    total: int
    page: int
    per_page: int