from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


def get_camera(db: Session, camera_id: int) -> Optional[Camera]:
    """Get camera by ID"""
    return db.query(Camera).filter(Camera.id == camera_id).first()


def get_camera_by_name(db: Session, name: str) -> Optional[Camera]:
    """Get camera by name"""
    return db.query(Camera).filter(Camera.name == name).first()


def get_cameras(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    camera_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_recording: Optional[bool] = None,
    detection_enabled: Optional[bool] = None,
    search: Optional[str] = None
) -> list[Camera]:
    """Get multiple cameras with optional filters"""
    query = db.query(Camera)
    
    if location:
        query = query.filter(Camera.location.ilike(f"%{location}%"))
    
    if camera_type:
        query = query.filter(Camera.camera_type == camera_type)
    
    if is_active is not None:
        query = query.filter(Camera.is_active == is_active)
    
    if is_recording is not None:
        query = query.filter(Camera.is_recording == is_recording)
    
    if detection_enabled is not None:
        query = query.filter(Camera.detection_enabled == detection_enabled)
    
    if search:
        search_filter = or_(
            Camera.name.ilike(f"%{search}%"),
            Camera.location.ilike(f"%{search}%"),
            Camera.ip_address.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.offset(skip).limit(limit).all()


def count_cameras(
    db: Session,
    location: Optional[str] = None,
    camera_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_recording: Optional[bool] = None,
    detection_enabled: Optional[bool] = None,
    search: Optional[str] = None
) -> int:
    """Count cameras with optional filters"""
    query = db.query(Camera)
    
    if location:
        query = query.filter(Camera.location.ilike(f"%{location}%"))
    
    if camera_type:
        query = query.filter(Camera.camera_type == camera_type)
    
    if is_active is not None:
        query = query.filter(Camera.is_active == is_active)
    
    if is_recording is not None:
        query = query.filter(Camera.is_recording == is_recording)
    
    if detection_enabled is not None:
        query = query.filter(Camera.detection_enabled == detection_enabled)
    
    if search:
        search_filter = or_(
            Camera.name.ilike(f"%{search}%"),
            Camera.location.ilike(f"%{search}%"),
            Camera.ip_address.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.count()


def create_camera(db: Session, camera: CameraCreate, created_by: int) -> Camera:
    """Create new camera"""
    db_camera = Camera(
        name=camera.name,
        location=camera.location,
        ip_address=camera.ip_address,
        port=camera.port,
        stream_url=camera.stream_url,
        camera_type=camera.camera_type,
        resolution=camera.resolution,
        fps=camera.fps,
        latitude=camera.latitude,
        longitude=camera.longitude,
        is_active=camera.is_active,
        is_recording=camera.is_recording,
        detection_enabled=camera.detection_enabled,
        ppe_detection=camera.ppe_detection,
        pose_detection=camera.pose_detection,
        face_recognition=camera.face_recognition,
        description=camera.description,
        created_by=created_by
    )
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


def update_camera(
    db: Session, 
    camera_id: int, 
    camera_update: CameraUpdate
) -> Optional[Camera]:
    """Update camera"""
    db_camera = get_camera(db, camera_id)
    if not db_camera:
        return None
    
    update_data = camera_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_camera, field, value)
    
    db.commit()
    db.refresh(db_camera)
    return db_camera


def delete_camera(db: Session, camera_id: int) -> bool:
    """Delete camera (soft delete by setting is_active to False)"""
    db_camera = get_camera(db, camera_id)
    if not db_camera:
        return False
    
    db_camera.is_active = False
    db.commit()
    return True


def get_active_cameras(db: Session) -> list[Camera]:
    """Get all active cameras"""
    return db.query(Camera).filter(Camera.is_active == True).all()


def get_recording_cameras(db: Session) -> list[Camera]:
    """Get all cameras that are currently recording"""
    return db.query(Camera).filter(
        and_(Camera.is_active == True, Camera.is_recording == True)
    ).all()


def get_camera_locations(db: Session) -> list[str]:
    """Get all unique camera locations"""
    result = db.query(Camera.location).distinct().all()
    return [loc[0] for loc in result if loc[0]]


def update_camera_last_seen(db: Session, camera_id: int) -> bool:
    """Update camera last_seen timestamp"""
    db_camera = get_camera(db, camera_id)
    if not db_camera:
        return False
    
    from datetime import datetime
    db_camera.last_seen = datetime.utcnow()
    db.commit()
    return True