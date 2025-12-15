import os
import sys

# Ensure project root is on sys.path so "app" package is importable
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.db.session import SessionLocal, engine  # type: ignore
from app.db.base import Base  # type: ignore  # imports all models via base
from app.models.role import Role  # type: ignore
from app.models.user import User  # type: ignore
from app.models.camera import Camera  # type: ignore
from app.core.security import get_password_hash  # type: ignore


def main():
    # Ensure tables exist before seeding
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[WARNING] Could not create tables automatically: {e}")

    db = SessionLocal()
    try:
        # Ensure roles exist
        roles_data = [
            {"name": "Admin", "description": "System Administrator", "is_active": True},
            {"name": "Manager", "description": "Department Manager", "is_active": True},
            {"name": "AssistantManager", "description": "Assistant Manager", "is_active": True},
            {"name": "HSEExpert", "description": "Health Safety Environment Expert", "is_active": True},
        ]
        for data in roles_data:
            role = db.query(Role).filter(Role.name == data["name"]).first()
            if not role:
                role = Role(**data)
                db.add(role)
        db.commit()

        # Create admin user if missing
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        admin = db.query(User).filter(User.email == "admin@isg.com").first()
        if not admin and admin_role:
            admin = User(
                email="admin@isg.com",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
                role_id=admin_role.id,
            )
            db.add(admin)
            db.commit()
            print("[SUCCESS] Admin user created: admin@isg.com / admin123")
        else:
            print("[INFO] Admin user already exists or Admin role missing.")
        
        # Seed demo cameras if admin exists
        if admin or db.query(User).filter(User.email == "admin@isg.com").first():
            seed_cameras(db)
    finally:
        db.close()


def seed_cameras(db):
    """Seed demo cameras that correspond to demo video files"""
    admin = db.query(User).filter(User.email == "admin@isg.com").first()
    if not admin:
        print("[WARNING] Cannot seed cameras - admin user not found")
        return
    
    # Define demo cameras
    cameras_data = [
        {
            "id": 1,
            "name": "Camera-1",
            "location": "Main Floor - Factory Area 1",
            "stream_url": "api/v1/cameras/1/stream",
            "camera_type": "demo",
            "description": "Demo camera streaming demo.mp4",
        },
        {
            "id": 2,
            "name": "Camera-2",
            "location": "Assembly Line - Factory Area 2",
            "stream_url": "api/v1/cameras/2/stream",
            "camera_type": "demo",
            "description": "Demo camera streaming demo2.mp4",
        },
        {
            "id": 3,
            "name": "Camera-3",
            "location": "Storage Area - Factory Area 3",
            "stream_url": "api/v1/cameras/3/stream",
            "camera_type": "demo",
            "description": "Demo camera streaming demo3.mp4",
        },
    ]
    
    created_count = 0
    for data in cameras_data:
        camera = db.query(Camera).filter(Camera.name == data["name"]).first()
        if not camera:
            camera = Camera(
                id=data["id"],
                name=data["name"],
                location=data["location"],
                stream_url=data["stream_url"],
                camera_type=data["camera_type"],
                description=data["description"],
                resolution="1920x1080",
                fps=30,
                is_active=True,
                is_recording=False,
                detection_enabled=True,
                ppe_detection=True,
                pose_detection=True,
                face_recognition=True,
                created_by=admin.id,
            )
            db.add(camera)
            created_count += 1
    
    if created_count > 0:
        db.commit()
        print(f"[SUCCESS] Created {created_count} demo camera(s)")


if __name__ == "__main__":
    main()
