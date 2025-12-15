import os
import sys

# Ensure project root is on sys.path so "app" package is importable
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.db.session import SessionLocal, engine  # type: ignore
from app.db.base import Base  # type: ignore
from app.models.camera import Camera  # type: ignore
from app.models.user import User  # type: ignore


def main():
    """Seed demo cameras that correspond to demo video files (demo.mp4, demo2.mp4, demo3.mp4)"""
    
    db = SessionLocal()
    try:
        # Get the admin user to use as created_by
        admin = db.query(User).filter(User.email == "admin@isg.com").first()
        if not admin:
            print("[ERROR] Admin user not found. Please run seed_admin.py first.")
            return
        
        # Define demo cameras that match the video files
        cameras_data = [
            {
                "name": "Camera-1",
                "location": "Main Floor - Factory Area 1",
                "stream_url": "api/v1/cameras/1/stream",
                "camera_type": "demo",
                "description": "Demo camera streaming demo.mp4",
                "resolution": "1920x1080",
                "fps": 30,
                "is_active": True,
                "is_recording": False,
                "detection_enabled": True,
                "ppe_detection": True,
                "pose_detection": True,
                "face_recognition": True,
            },
            {
                "name": "Camera-2",
                "location": "Assembly Line - Factory Area 2",
                "stream_url": "api/v1/cameras/2/stream",
                "camera_type": "demo",
                "description": "Demo camera streaming demo2.mp4",
                "resolution": "1920x1080",
                "fps": 30,
                "is_active": True,
                "is_recording": False,
                "detection_enabled": True,
                "ppe_detection": True,
                "pose_detection": True,
                "face_recognition": True,
            },
            {
                "name": "Camera-3",
                "location": "Storage Area - Factory Area 3",
                "stream_url": "api/v1/cameras/3/stream",
                "camera_type": "demo",
                "description": "Demo camera streaming demo3.mp4",
                "resolution": "1920x1080",
                "fps": 30,
                "is_active": True,
                "is_recording": False,
                "detection_enabled": True,
                "ppe_detection": True,
                "pose_detection": True,
                "face_recognition": True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for idx, data in enumerate(cameras_data, start=1):
            # Check if camera already exists by name
            camera = db.query(Camera).filter(Camera.name == data["name"]).first()
            
            if camera:
                # Update existing camera
                for key, value in data.items():
                    if key != "created_by":
                        setattr(camera, key, value)
                updated_count += 1
                print(f"[UPDATED] Camera: {data['name']}")
            else:
                # Create new camera with specific ID to match the hardcoded camera IDs
                camera = Camera(
                    id=idx,  # Use 1, 2, 3 to match the hardcoded IDs in the frontend
                    created_by=admin.id,
                    **data
                )
                db.add(camera)
                created_count += 1
                print(f"[CREATED] Camera: {data['name']}")
        
        db.commit()
        print(f"\n[SUCCESS] Cameras seeded successfully!")
        print(f"  - Created: {created_count}")
        print(f"  - Updated: {updated_count}")
        print(f"  - Total: {created_count + updated_count}")
        print("\nThese cameras can now be assigned to factory areas.")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to seed cameras: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
