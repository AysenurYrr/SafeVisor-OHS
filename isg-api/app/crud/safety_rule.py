from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.safety_rule import SafetyRule, SafetyRuleType
from app.schemas.safety_rule import SafetyRuleCreate, SafetyRuleUpdate


def get_rules(
    db: Session,
    factory_area_id: Optional[int] = None,
    camera_id: Optional[int] = None,
) -> List[SafetyRule]:
    query = db.query(SafetyRule)
    if factory_area_id is not None:
        query = query.filter(SafetyRule.factory_area_id == factory_area_id)
    if camera_id is not None:
        query = query.filter(SafetyRule.camera_id == camera_id)
    return query.all()


def get_rule(db: Session, rule_id: int) -> Optional[SafetyRule]:
    return db.query(SafetyRule).filter(SafetyRule.id == rule_id).first()


def upsert_rule(db: Session, rule: SafetyRuleCreate) -> SafetyRule:
    existing = (
        db.query(SafetyRule)
        .filter(
            SafetyRule.rule_type == rule.rule_type,
            SafetyRule.factory_area_id == rule.factory_area_id,
            SafetyRule.camera_id == rule.camera_id,
        )
        .first()
    )
    if existing:
        existing.enabled = rule.enabled
        existing.min_duration_sec = rule.min_duration_sec
        existing.cooldown_sec = rule.cooldown_sec
        existing.confidence_threshold = rule.confidence_threshold
        existing.scope = rule.scope
        db.commit()
        db.refresh(existing)
        return existing

    db_rule = SafetyRule(
        factory_area_id=rule.factory_area_id,
        camera_id=rule.camera_id,
        rule_type=rule.rule_type,
        enabled=rule.enabled,
        min_duration_sec=rule.min_duration_sec,
        cooldown_sec=rule.cooldown_sec,
        confidence_threshold=rule.confidence_threshold,
        scope=rule.scope,
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


def replace_rules_for_area(db: Session, area_id: int, rules: List[SafetyRuleCreate]) -> List[SafetyRule]:
    db.query(SafetyRule).filter(SafetyRule.factory_area_id == area_id, SafetyRule.camera_id == None).delete()
    created: List[SafetyRule] = []
    for rule in rules:
        payload = SafetyRuleCreate(
            **rule.model_dump(),
            factory_area_id=area_id,
            camera_id=rule.camera_id,
        )
        created.append(upsert_rule(db, payload))
    return created


def replace_rules_for_camera(db: Session, camera_id: int, rules: List[SafetyRuleCreate]) -> List[SafetyRule]:
    db.query(SafetyRule).filter(SafetyRule.camera_id == camera_id).delete()
    created: List[SafetyRule] = []
    for rule in rules:
        payload = SafetyRuleCreate(
            **rule.model_dump(),
            camera_id=camera_id,
        )
        created.append(upsert_rule(db, payload))
    return created


def delete_rule(db: Session, rule_id: int) -> bool:
    rule = get_rule(db, rule_id)
    if not rule:
        return False
    db.delete(rule)
    db.commit()
    return True
