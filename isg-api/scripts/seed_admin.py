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
    finally:
        db.close()


if __name__ == "__main__":
    main()
