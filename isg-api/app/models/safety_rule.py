import enum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class RuleScope(str, enum.Enum):
    PER_PERSON = "per_person"
    PER_CAMERA = "per_camera"


class SafetyRuleType(str, enum.Enum):
    HELMET = "helmet"
    VEST = "vest"
    GLOVES = "gloves"
    GLASSES = "glasses"
    MASK = "mask"
    BOOTS = "boots"
    SUIT = "safety-suit"
    FACE = "face"


class SafetyRule(Base):
    __tablename__ = "safety_rules"

    id = Column(Integer, primary_key=True, index=True)
    factory_area_id = Column(Integer, ForeignKey("factory_areas.id", ondelete="SET NULL"), nullable=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    rule_type = Column(Enum(SafetyRuleType), nullable=False)
    enabled = Column(Boolean, default=True)
    min_duration_sec = Column(Integer, default=10)
    cooldown_sec = Column(Integer, default=60)
    confidence_threshold = Column(Float, default=0.5)
    scope = Column(Enum(RuleScope), default=RuleScope.PER_PERSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "factory_area_id",
            "camera_id",
            "rule_type",
            name="uq_safety_rule_scope",
        ),
    )

    factory_area = relationship("FactoryArea", back_populates="safety_rules")
    camera = relationship("Camera", back_populates="safety_rules")
