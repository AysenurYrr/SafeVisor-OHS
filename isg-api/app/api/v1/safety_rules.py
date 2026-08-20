from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import safety_rule as crud_safety_rule
from app.schemas.safety_rule import SafetyRuleCreate, SafetyRuleResponse, SafetyRuleUpdate
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[SafetyRuleResponse])
def list_rules(
    db: Session = Depends(deps.get_db),
    camera_id: Optional[int] = Query(None),
    factory_area_id: Optional[int] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[SafetyRuleResponse]:
    return crud_safety_rule.get_rules(db, factory_area_id=factory_area_id, camera_id=camera_id)


@router.post("/", response_model=SafetyRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_in: SafetyRuleCreate,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> SafetyRuleResponse:
    return crud_safety_rule.upsert_rule(db, rule_in)


@router.put("/{rule_id}", response_model=SafetyRuleResponse)
def update_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_id: int,
    rule_update: SafetyRuleUpdate,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> SafetyRuleResponse:
    rule = crud_safety_rule.get_rule(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Safety rule not found")
    data = SafetyRuleCreate(
        rule_type=rule.rule_type,
        enabled=rule_update.enabled if rule_update.enabled is not None else rule.enabled,
        min_duration_sec=rule_update.min_duration_sec if rule_update.min_duration_sec is not None else rule.min_duration_sec,
        cooldown_sec=rule_update.cooldown_sec if rule_update.cooldown_sec is not None else rule.cooldown_sec,
        confidence_threshold=rule_update.confidence_threshold if rule_update.confidence_threshold is not None else rule.confidence_threshold,
        scope=rule_update.scope if rule_update.scope is not None else rule.scope,
        factory_area_id=rule.factory_area_id,
        camera_id=rule.camera_id,
    )
    return crud_safety_rule.upsert_rule(db, data)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_id: int,
    current_user: User = Depends(deps.check_manager_or_admin_role),
) -> None:
    deleted = crud_safety_rule.delete_rule(db, rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Safety rule not found")
    return None
