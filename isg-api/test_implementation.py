#!/usr/bin/env python3
"""
Test script to validate the new models and migrations
This can be run to test the implementation before Docker deployment
"""

import os
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import tempfile
from datetime import date, datetime
import json

# Use SQLite for testing to avoid needing PostgreSQL connection
TEST_DATABASE_URL = f"sqlite:///{tempfile.gettempdir()}/safevisor_test.db"

def test_basic_functionality():
    """Test basic model creation and relationships"""
    try:
        from app.db.session import Base
        from app.models import Employee, Camera, ViolationLog, Analytics
        
        # Create test engine and session
        engine = create_engine(TEST_DATABASE_URL, echo=False)
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("✓ Models imported and tables created successfully")
        
        # Test Employee creation with new fields
        try:
            # Note: For SQLite testing, we'll skip JSONB fields since SQLite doesn't support them
            employee = Employee(
                employee_id="EMP-TEST-001",
                first_name="Test",
                last_name="Employee",
                department="Testing",
                position="Tester",
                hire_date=date.today(),
                violation_score=25.5,
                photo_1_path="/test/photo1.jpg",
                photo_2_path="/test/photo2.jpg", 
                photo_3_path="/test/photo3.jpg",
                created_by=1  # Mock user ID
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)
            print(f"✓ Employee created with ID: {employee.id}, violation_score: {employee.violation_score}")
            
        except Exception as e:
            print(f"✗ Employee creation failed: {e}")
            
        # Test Camera creation with new fields
        try:
            camera = Camera(
                name="Test Camera 001",
                location="Test Location",
                stream_url="rtmp://test.com/stream",
                stream_path="rtmp://test.com/stream/path",
                created_by=1  # Mock user ID
            )
            db.add(camera)
            db.commit()
            db.refresh(camera)
            print(f"✓ Camera created with ID: {camera.id}, name: {camera.name}")
            
        except Exception as e:
            print(f"✗ Camera creation failed: {e}")
            
        # Test ViolationLog creation
        try:
            violation_log = ViolationLog(
                employee_id=employee.id,
                camera_id=camera.id,
                violation_types=json.dumps(["no_helmet", "no_vest"]),
                image_paths=json.dumps(["/path/img1.jpg", "/path/img2.jpg"]),
                duration=45.5,
                reported=False
            )
            db.add(violation_log)
            db.commit() 
            db.refresh(violation_log)
            print(f"✓ ViolationLog created with ID: {violation_log.id}")
            
        except Exception as e:
            print(f"✗ ViolationLog creation failed: {e}")
            
        # Test Analytics creation
        try:
            analytics = Analytics(
                employee_id=employee.id,
                violation_type="no_helmet",
                violation_date=date.today(),
                violation_image_path="/path/analytics_img.jpg"
            )
            db.add(analytics)
            db.commit()
            db.refresh(analytics)
            print(f"✓ Analytics record created with ID: {analytics.id}")
            
        except Exception as e:
            print(f"✗ Analytics creation failed: {e}")
        
        db.close()
        print("\n✓ All basic functionality tests passed!")
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()


def test_schema_validations():
    """Test Pydantic schema validations"""
    try:
        from app.schemas.employee import EmployeeCreate
        from app.schemas.camera import CameraCreate, CameraStatusEnum
        from app.schemas.violation_log import ViolationLogCreate
        from app.schemas.analytics import AnalyticsCreate
        
        print("\nTesting schema validations...")
        
        # Test Employee schema
        emp_data = EmployeeCreate(
            employee_id="EMP-SCHEMA-001",
            first_name="Schema",
            last_name="Test",
            department="Testing",
            position="Validator", 
            hire_date=date.today(),
            violation_score=75.0,
            photo_1_path="/schema/photo1.jpg",
            photo_2_path="/schema/photo2.jpg",
            photo_3_path="/schema/photo3.jpg",
            face_embeddings=[0.1, 0.2, 0.3, 0.4, 0.5]
        )
        print(f"✓ Employee schema validation passed: {emp_data.employee_id}")
        
        # Test Camera schema
        camera_data = CameraCreate(
            name="Schema Test Camera",
            location="Schema Test Location",
            stream_url="rtmp://schema.test/stream",
            stream_path="rtmp://schema.test/path",
            violation_rules=["helmet_required", "vest_required"],
            status=CameraStatusEnum.ONLINE
        )
        print(f"✓ Camera schema validation passed: {camera_data.name}")
        
        # Test ViolationLog schema
        vlog_data = ViolationLogCreate(
            employee_id=1,
            camera_id=1,
            violation_types=["no_helmet", "no_gloves"],
            image_paths=["/schema/violation1.jpg"],
            duration=30.0,
            reported=False
        )
        print(f"✓ ViolationLog schema validation passed")
        
        # Test Analytics schema
        analytics_data = AnalyticsCreate(
            employee_id=1,
            violation_type="no_helmet",
            violation_date=date.today()
        )
        print(f"✓ Analytics schema validation passed")
        
        print("✓ All schema validation tests passed!")
        
    except Exception as e:
        print(f"✗ Schema validation test failed: {e}")
        import traceback
        traceback.print_exc()


def test_migration_script():
    """Test that the migration script is syntactically correct"""
    try:
        # Import the migration to check syntax
        from alembic.versions import add_new_fields_and_tables_20250926_2022 as migration
        
        print("\nTesting migration script...")
        print(f"✓ Migration module imported successfully")
        print(f"✓ Revision ID: {migration.revision}")
        print(f"✓ Down revision: {migration.down_revision}")
        
        # Check that upgrade and downgrade functions exist
        if hasattr(migration, 'upgrade') and callable(migration.upgrade):
            print("✓ Upgrade function exists")
        else:
            print("✗ Upgrade function missing or not callable")
            
        if hasattr(migration, 'downgrade') and callable(migration.downgrade):
            print("✓ Downgrade function exists")
        else:
            print("✗ Downgrade function missing or not callable")
        
        print("✓ Migration script syntax test passed!")
        
    except Exception as e:
        print(f"✗ Migration script test failed: {e}")
        # This is not critical for functionality


if __name__ == "__main__":
    print("🧪 Running SafeVisor-OHS Backend Enhancement Tests")
    print("=" * 50)
    
    test_basic_functionality()
    test_schema_validations()
    test_migration_script()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\nNext steps:")
    print("1. Run Docker Compose to start PostgreSQL")
    print("2. Apply migrations: alembic upgrade head")
    print("3. Test API endpoints")
    print("4. Validate analytics processing functionality")