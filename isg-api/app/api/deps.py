from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.crud import user as crud_user

# Security scheme
security_scheme = HTTPBearer()


def get_db() -> Generator:
    """Get database session"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = security.verify_token(token.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: int = int(payload)
    except (ValueError, TypeError):
        raise credentials_exception
    
    user = crud_user.get_user(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not crud_user.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current superuser"""
    if not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges"
        )
    return current_user


def check_user_role(required_roles: list[str]):
    """
    Dependency factory to check if user has required role
    Usage: Depends(check_user_role(["Admin", "Manager"]))
    """
    def role_checker(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        # Get user's role name
        user_role_name = current_user.role.name if current_user.role else None
        
        if user_role_name not in required_roles and not crud_user.is_superuser(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of these roles: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker


def check_admin_role(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Check if user has Admin role"""
    user_role_name = current_user.role.name if current_user.role else None
    
    if user_role_name != "Admin" and not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


def check_manager_or_admin_role(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Check if user has Manager or Admin role"""
    user_role_name = current_user.role.name if current_user.role else None
    
    allowed_roles = ["Admin", "Manager"]
    if user_role_name not in allowed_roles and not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Admin access required"
        )
    
    return current_user


def check_hse_expert_access(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Check if user has HSE Expert, Manager, or Admin role"""
    user_role_name = current_user.role.name if current_user.role else None
    
    allowed_roles = ["Admin", "Manager", "HSEExpert"]
    if user_role_name not in allowed_roles and not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HSE Expert, Manager, or Admin access required"
        )
    
    return current_user


def get_optional_current_user(
    db: Session = Depends(get_db),
    token: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Optional[User]:
    """Get current user if token is provided, otherwise return None"""
    if not token:
        return None
    
    try:
        payload = security.verify_token(token.credentials)
        if payload is None:
            return None
        
        user_id: int = int(payload)
        user = crud_user.get_user(db, user_id=user_id)
        return user if user and crud_user.is_active(user) else None
    except (ValueError, TypeError):
        return None