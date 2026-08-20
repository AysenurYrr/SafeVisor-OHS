from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

from app.schemas.safety_rule import SafetyRuleCreate, SafetyRuleResponse


# Valid safety rules that can be assigned to a factory area
VALID_SAFETY_RULES = [
    "glasses",
    "face-mask",
    "ear-muffs",
    "hands",
    "gloves",
    "safety-vest",
    "tools",
    "helmet",
    "medical-suit",
    "safety-suit"
]


class FactoryAreaBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class FactoryAreaCreate(FactoryAreaBase):
    camera_ids: List[int] = []
    safety_rules: List[str] = []
    rule_configs: Optional[List[SafetyRuleCreate]] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Area name must be at least 3 characters long')
        return v
    
    @validator('safety_rules')
    def validate_safety_rules(cls, v):
        if v:
            invalid_rules = [rule for rule in v if rule not in VALID_SAFETY_RULES]
            if invalid_rules:
                raise ValueError(f'Invalid safety rules: {", ".join(invalid_rules)}. Valid rules are: {", ".join(VALID_SAFETY_RULES)}')
        return v


class FactoryAreaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    camera_ids: Optional[List[int]] = None
    safety_rules: Optional[List[str]] = None
    rule_configs: Optional[List[SafetyRuleCreate]] = None
    
    @validator('safety_rules')
    def validate_safety_rules(cls, v):
        if v is not None:
            invalid_rules = [rule for rule in v if rule not in VALID_SAFETY_RULES]
            if invalid_rules:
                raise ValueError(f'Invalid safety rules: {", ".join(invalid_rules)}. Valid rules are: {", ".join(VALID_SAFETY_RULES)}')
        return v


class CameraBasicInfo(BaseModel):
    id: int
    name: str
    location: str
    stream_url: str
    is_active: bool
    
    class Config:
        from_attributes = True


class FactoryAreaResponse(FactoryAreaBase):
    id: int
    cameras: List[CameraBasicInfo] = []
    safety_rules: List[str] = []
    rule_configs: List[SafetyRuleResponse] = []
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FactoryAreaListResponse(BaseModel):
    areas: List[FactoryAreaResponse]
    total: int
    page: int
    per_page: int
