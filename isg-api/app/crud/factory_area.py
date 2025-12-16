from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text
from app.models.factory_area import FactoryArea, area_rules
from app.models.camera import Camera
from app.models.safety_rule import SafetyRule, SafetyRuleType
from app.schemas.factory_area import FactoryAreaCreate, FactoryAreaUpdate
from app.schemas.safety_rule import SafetyRuleCreate
from app.crud import safety_rule as crud_safety_rule


def get_factory_area(db: Session, area_id: int) -> Optional[FactoryArea]:
    """Get factory area by ID"""
    return db.query(FactoryArea).filter(FactoryArea.id == area_id).first()


def get_factory_area_by_name(db: Session, name: str) -> Optional[FactoryArea]:
    """Get factory area by name"""
    return db.query(FactoryArea).filter(FactoryArea.name == name).first()


def get_factory_areas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> List[FactoryArea]:
    """Get multiple factory areas with optional filters"""
    query = db.query(FactoryArea)
    
    if is_active is not None:
        query = query.filter(FactoryArea.is_active == is_active)
    
    if search:
        search_filter = or_(
            FactoryArea.name.ilike(f"%{search}%"),
            FactoryArea.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.offset(skip).limit(limit).all()


def count_factory_areas(
    db: Session,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> int:
    """Count factory areas with optional filters"""
    query = db.query(FactoryArea)
    
    if is_active is not None:
        query = query.filter(FactoryArea.is_active == is_active)
    
    if search:
        search_filter = or_(
            FactoryArea.name.ilike(f"%{search}%"),
            FactoryArea.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.count()


def get_area_safety_rules(db: Session, area_id: int) -> List[str]:
    """Get safety rules for a factory area (fall back to legacy table if needed)."""
    rules = crud_safety_rule.get_rules(db, factory_area_id=area_id)
    if rules:
        return [r.rule_type.value for r in rules if r.enabled]

    # Legacy fallback
    result = db.execute(
        text("SELECT rule_name FROM area_rules WHERE area_id = :area_id"),
        {"area_id": area_id}
    )
    return [row[0] for row in result.fetchall()]


def create_factory_area(
    db: Session, 
    area: FactoryAreaCreate, 
    created_by: int
) -> FactoryArea:
    """Create new factory area"""
    db_area = FactoryArea(
        name=area.name,
        description=area.description,
        is_active=area.is_active,
        created_by=created_by
    )
    db.add(db_area)
    db.flush()  # Get the ID without committing
    
    # Link cameras to this area (one-to-many)
    if area.camera_ids:
        cameras = db.query(Camera).filter(Camera.id.in_(area.camera_ids)).all()
        for camera in cameras:
            # Check if camera is already linked to another area
            if camera.factory_area_id is not None and camera.factory_area_id != db_area.id:
                raise ValueError(f"Camera '{camera.name}' is already linked to another factory area")
            camera.factory_area_id = db_area.id
    
    # Add safety rules
    if area.rule_configs:
        for rule_cfg in area.rule_configs:
            payload = SafetyRuleCreate(**rule_cfg.model_dump(), factory_area_id=db_area.id)
            crud_safety_rule.upsert_rule(db, payload)
    elif area.safety_rules:
        # Backwards compatible defaults
        for rule in area.safety_rules:
            db.execute(
                text("INSERT INTO area_rules (area_id, rule_name) VALUES (:area_id, :rule_name)"),
                {"area_id": db_area.id, "rule_name": rule}
            )
            try:
                payload = SafetyRuleCreate(
                    rule_type=SafetyRuleType(rule),
                    factory_area_id=db_area.id,
                    min_duration_sec=10,
                    cooldown_sec=60,
                    confidence_threshold=0.5,
                )
                crud_safety_rule.upsert_rule(db, payload)
            except Exception:
                # Rule may not map to enum; keep legacy value only
                pass
    
    db.commit()
    db.refresh(db_area)
    return db_area


def update_factory_area(
    db: Session, 
    area_id: int, 
    area_update: FactoryAreaUpdate
) -> Optional[FactoryArea]:
    """Update factory area"""
    db_area = get_factory_area(db, area_id)
    if not db_area:
        return None
    
    update_data = area_update.model_dump(exclude_unset=True, exclude={'camera_ids', 'safety_rules', 'rule_configs'})
    
    # Update basic fields
    for field, value in update_data.items():
        setattr(db_area, field, value)
    
    # Update cameras if provided (one-to-many)
    if area_update.camera_ids is not None:
        # First, unlink all current cameras
        current_cameras = db.query(Camera).filter(Camera.factory_area_id == area_id).all()
        for camera in current_cameras:
            camera.factory_area_id = None
        
        # Then link new cameras
        if area_update.camera_ids:
            cameras = db.query(Camera).filter(Camera.id.in_(area_update.camera_ids)).all()
            for camera in cameras:
                # Check if camera is already linked to another area
                if camera.factory_area_id is not None and camera.factory_area_id != area_id:
                    raise ValueError(f"Camera '{camera.name}' is already linked to another factory area")
                camera.factory_area_id = area_id
    
    # Update safety rules if provided
    if area_update.rule_configs is not None:
        db.query(SafetyRule).filter(
            SafetyRule.factory_area_id == area_id,
            SafetyRule.camera_id == None,
        ).delete()
        for rule_cfg in area_update.rule_configs:
            payload = SafetyRuleCreate(**rule_cfg.model_dump(), factory_area_id=area_id)
            crud_safety_rule.upsert_rule(db, payload)
    elif area_update.safety_rules is not None:
        # Legacy payload support
        db.execute(
            text("DELETE FROM area_rules WHERE area_id = :area_id"),
            {"area_id": area_id}
        )
        for rule in area_update.safety_rules:
            db.execute(
                text("INSERT INTO area_rules (area_id, rule_name) VALUES (:area_id, :rule_name)"),
                {"area_id": area_id, "rule_name": rule}
            )
            try:
                payload = SafetyRuleCreate(
                    rule_type=SafetyRuleType(rule),
                    factory_area_id=area_id,
                    min_duration_sec=10,
                    cooldown_sec=60,
                    confidence_threshold=0.5,
                )
                crud_safety_rule.upsert_rule(db, payload)
            except Exception:
                pass
    
    db.commit()
    db.refresh(db_area)
    return db_area


def delete_factory_area(db: Session, area_id: int) -> bool:
    """Delete factory area (soft delete by setting is_active to False)"""
    db_area = get_factory_area(db, area_id)
    if not db_area:
        return False
    
    db_area.is_active = False
    db.commit()
    return True


def hard_delete_factory_area(db: Session, area_id: int) -> bool:
    """Permanently delete factory area"""
    db_area = get_factory_area(db, area_id)
    if not db_area:
        return False
    
    # Delete associated rules (should cascade, but being explicit)
    db.execute(
        text("DELETE FROM area_rules WHERE area_id = :area_id"),
        {"area_id": area_id}
    )
    
    # Delete the area
    db.delete(db_area)
    db.commit()
    return True


def get_active_factory_areas(db: Session) -> List[FactoryArea]:
    """Get all active factory areas"""
    return db.query(FactoryArea).filter(FactoryArea.is_active == True).all()
