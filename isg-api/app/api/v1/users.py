from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import user as crud_user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(deps.check_admin_role),
) -> List[UserResponse]:
    """
    Retrieve users (Admin only)
    """
    users = crud_user.get_users(
        db, skip=skip, limit=limit, is_active=is_active
    )
    return users


@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.check_admin_role),
) -> UserResponse:
    """
    Create new user (Admin only)
    """
    # Check if user with email already exists
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Check if user with username already exists
    user = crud_user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    try:
        user = crud_user.create_user(db, user=user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> UserResponse:
    """
    Get a specific user by ID
    """
    # Users can only see their own profile unless they're admin
    if user_id != current_user.id and not crud_user.is_superuser(current_user):
        user_role_name = current_user.role.name if current_user.role else None
        if user_role_name != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> UserResponse:
    """
    Update a user
    """
    # Users can only update their own profile unless they're admin
    if user_id != current_user.id and not crud_user.is_superuser(current_user):
        user_role_name = current_user.role.name if current_user.role else None
        if user_role_name != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check email uniqueness if updating email
    if user_in.email and user_in.email != user.email:
        existing_user = crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )
    
    # Check username uniqueness if updating username
    if user_in.username and user_in.username != user.username:
        existing_user = crud_user.get_user_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this username already exists"
            )
    
    try:
        user = crud_user.update_user(db, user_id=user_id, user_update=user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.check_admin_role),
) -> dict:
    """
    Delete a user (Admin only)
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )
    
    success = crud_user.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete user"
        )
    
    return {"message": "User deleted successfully"}