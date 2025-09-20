from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    is_active: bool = True
    role_id: int
    profile_image: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    profile_image: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    password: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if v and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_superuser: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int
    is_superuser: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None