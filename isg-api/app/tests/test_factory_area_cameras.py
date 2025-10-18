"""
Test factory area camera management functionality
"""
import pytest
from sqlalchemy.orm import Session
from app.models.camera import Camera
from app.models.factory_area import FactoryArea
from app.models.user import User
from app.crud import factory_area as crud_factory_area
from app.schemas.factory_area import FactoryAreaCreate, FactoryAreaUpdate


def test_create_factory_area_with_cameras(db: Session, admin_user: User):
    """Test creating a factory area with camera assignments"""
    # Create test cameras first
    cameras = []
    for i in range(1, 4):
        camera = Camera(
            id=i,
            name=f"Test-Camera-{i}",
            location=f"Test Location {i}",
            stream_url=f"/api/v1/cameras/{i}/stream",
            camera_type="test",
            description=f"Test camera {i}",
            resolution="1920x1080",
            fps=30,
            is_active=True,
            created_by=admin_user.id,
        )
        db.add(camera)
        cameras.append(camera)
    db.commit()
    
    # Create factory area with cameras
    area_data = FactoryAreaCreate(
        name="Test Factory Area",
        description="Test area with cameras",
        camera_ids=[1, 2],
        safety_rules=["helmet", "safety-vest"],
        is_active=True
    )
    
    area = crud_factory_area.create_factory_area(
        db=db,
        area=area_data,
        created_by=admin_user.id
    )
    
    # Verify area was created
    assert area.id is not None
    assert area.name == "Test Factory Area"
    assert len(area.cameras) == 2
    assert area.cameras[0].name in ["Test-Camera-1", "Test-Camera-2"]
    assert area.cameras[1].name in ["Test-Camera-1", "Test-Camera-2"]
    
    # Verify safety rules
    rules = crud_factory_area.get_area_safety_rules(db, area.id)
    assert len(rules) == 2
    assert "helmet" in rules
    assert "safety-vest" in rules


def test_update_factory_area_cameras(db: Session, admin_user: User):
    """Test updating camera assignments for a factory area"""
    # Create test cameras
    for i in range(1, 4):
        camera = Camera(
            id=i,
            name=f"Test-Camera-{i}",
            location=f"Test Location {i}",
            stream_url=f"/api/v1/cameras/{i}/stream",
            camera_type="test",
            created_by=admin_user.id,
        )
        db.add(camera)
    db.commit()
    
    # Create factory area with camera 1 and 2
    area_data = FactoryAreaCreate(
        name="Test Area",
        camera_ids=[1, 2],
        is_active=True
    )
    area = crud_factory_area.create_factory_area(
        db=db,
        area=area_data,
        created_by=admin_user.id
    )
    assert len(area.cameras) == 2
    
    # Update to use camera 2 and 3 (remove 1, add 3)
    update_data = FactoryAreaUpdate(
        camera_ids=[2, 3]
    )
    updated_area = crud_factory_area.update_factory_area(
        db=db,
        area_id=area.id,
        area_update=update_data
    )
    
    # Verify update
    assert len(updated_area.cameras) == 2
    camera_ids = [c.id for c in updated_area.cameras]
    assert 2 in camera_ids
    assert 3 in camera_ids
    assert 1 not in camera_ids


def test_remove_all_cameras_from_area(db: Session, admin_user: User):
    """Test removing all camera assignments from a factory area"""
    # Create test camera
    camera = Camera(
        id=1,
        name="Test-Camera-1",
        location="Test Location",
        stream_url="/api/v1/cameras/1/stream",
        camera_type="test",
        created_by=admin_user.id,
    )
    db.add(camera)
    db.commit()
    
    # Create factory area with camera
    area_data = FactoryAreaCreate(
        name="Test Area",
        camera_ids=[1],
        is_active=True
    )
    area = crud_factory_area.create_factory_area(
        db=db,
        area=area_data,
        created_by=admin_user.id
    )
    assert len(area.cameras) == 1
    
    # Remove all cameras
    update_data = FactoryAreaUpdate(
        camera_ids=[]
    )
    updated_area = crud_factory_area.update_factory_area(
        db=db,
        area_id=area.id,
        area_update=update_data
    )
    
    # Verify all cameras removed
    assert len(updated_area.cameras) == 0


def test_factory_area_camera_display_count(db: Session, admin_user: User):
    """Test that camera count is correctly displayed"""
    # Create test cameras
    for i in range(1, 4):
        camera = Camera(
            id=i,
            name=f"Test-Camera-{i}",
            location=f"Test Location {i}",
            stream_url=f"/api/v1/cameras/{i}/stream",
            camera_type="test",
            created_by=admin_user.id,
        )
        db.add(camera)
    db.commit()
    
    # Create factory area with all 3 cameras
    area_data = FactoryAreaCreate(
        name="Test Area",
        camera_ids=[1, 2, 3],
        is_active=True
    )
    area = crud_factory_area.create_factory_area(
        db=db,
        area=area_data,
        created_by=admin_user.id
    )
    
    # Verify camera count
    assert len(area.cameras) == 3
    
    # Fetch area again to ensure cameras are persisted
    fetched_area = crud_factory_area.get_factory_area(db, area.id)
    assert fetched_area is not None
    assert len(fetched_area.cameras) == 3


# Fixtures would be defined in conftest.py
# Example fixture structure:
"""
@pytest.fixture
def db():
    # Setup test database session
    pass

@pytest.fixture
def admin_user(db):
    # Create and return admin user for testing
    pass
"""
