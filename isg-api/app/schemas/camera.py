from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CameraStatusEnum(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class CameraBase(BaseModel):
    name: str
    location: str
    ip_address: Optional[str] = None
    port: int = 554
    stream_url: str  # Keep for backward compatibility
    stream_path: str  # New required field
    camera_type: str = "ip"
    resolution: str = "1920x1080"
    fps: int = 30
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool = True
    is_recording: bool = False
    detection_enabled: bool = True
    ppe_detection: bool = True
    pose_detection: bool = True
    face_recognition: bool = True
    description: Optional[str] = None
    violation_rules: Optional[List[str]] = []  # e.g., ["helmet_required", "gloves_required"]
    status: CameraStatusEnum = CameraStatusEnum.UNKNOWN


class CameraCreate(CameraBase):
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Camera name must be at least 3 characters long')
        return v
    
    @field_validator('stream_url')
    @classmethod
    def validate_stream_url(cls, v):
        if not v:
            raise ValueError('Stream URL is required')
        return v
    
    @field_validator('stream_path')
    @classmethod
    def validate_stream_path(cls, v):
        if not v:
            raise ValueError('Stream path is required')
        return v


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    stream_url: Optional[str] = None
    stream_path: Optional[str] = None
    camera_type: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None
    is_recording: Optional[bool] = None
    detection_enabled: Optional[bool] = None
    ppe_detection: Optional[bool] = None
    pose_detection: Optional[bool] = None
    face_recognition: Optional[bool] = None
    description: Optional[str] = None
    violation_rules: Optional[List[str]] = None
    status: Optional[CameraStatusEnum] = None


class CameraInDB(CameraBase):
    id: int
    last_seen: Optional[datetime] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CameraResponse(CameraBase):
    id: int
    last_seen: Optional[datetime] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CameraListResponse(BaseModel):
    cameras: list[CameraResponse]
    total: int
    page: int
    per_page: int


class CameraStatus(BaseModel):
    id: int
    name: str
    is_active: bool
    is_recording: bool
    last_seen: Optional[datetime] = None
    status: CameraStatusEnum  # online, offline, unknown