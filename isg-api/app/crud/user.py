from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.crud.audit import log_action


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    is_active: Optional[bool] = None
) -> list[User]:
    """Get multiple users with optional filters"""
    query = db.query(User)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

# Backwards-compatible alias
list_users = get_users


def create_user(db: Session, user: UserCreate) -> User:
    """Create new user"""
    # Check if role exists
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise ValueError("Role not found")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username or user.email,
        full_name=user.full_name,
        password_hash=hashed_password,
        is_active=user.is_active,
        role_id=user.role_id,
        profile_image=user.profile_image,
        phone=user.phone,
        department=user.department,
        position=user.position
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    try:
        log_action(db, user_id=db_user.id, action="user_create", target=f"user:{db_user.id}")
    except Exception:
        pass
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    # Handle password update
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Check if role exists when updating role
    if "role_id" in update_data:
        role = db.query(Role).filter(Role.id == update_data["role_id"]).first()
        if not role:
            raise ValueError("Role not found")
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user (soft delete by setting is_active to False)"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db_user.is_active = False
    db.commit()
    try:
        log_action(db, user_id=user_id, action="user_delete", target=f"user:{user_id}")
    except Exception:
        pass
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def is_active(user: User) -> bool:
    """Check if user is active"""
    return user.is_active


def is_superuser(user: User) -> bool:
    """Check if user is superuser"""
    return user.is_superuser


def assign_role(db: Session, user: User, role: Role) -> None:
    if role not in user.roles:
        user.roles.append(role)
        db.commit()


def remove_role(db: Session, user: User, role: Role) -> None:
    if role in user.roles:
        user.roles.remove(role)
        db.commit()