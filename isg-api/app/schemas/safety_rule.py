from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.safety_rule import RuleScope, SafetyRuleType


class SafetyRuleBase(BaseModel):
    rule_type: SafetyRuleType = Field(..., description="Type of the safety rule (helmet, vest, gloves, etc.)")
    enabled: bool = True
    min_duration_sec: int = 10
    cooldown_sec: int = 60
    confidence_threshold: float = 0.5
    scope: RuleScope = RuleScope.PER_PERSON
    factory_area_id: Optional[int] = None
    camera_id: Optional[int] = None


class SafetyRuleCreate(SafetyRuleBase):
    pass


class SafetyRuleUpdate(BaseModel):
    enabled: Optional[bool] = None
    min_duration_sec: Optional[int] = None
    cooldown_sec: Optional[int] = None
    confidence_threshold: Optional[float] = None
    scope: Optional[RuleScope] = None


class SafetyRuleResponse(SafetyRuleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
