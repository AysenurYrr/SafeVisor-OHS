from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import user as crud_user
from app.models.user import User
from app.schemas.user import Token, UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud_user.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud_user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = security.create_refresh_token(
        user.id, expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(deps.get_db)
) -> Token:
    """
    Refresh access token using refresh token
    """
    try:
        payload = security.verify_refresh_token(refresh_token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        user_id: int = int(payload)
        user = crud_user.get_user(db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        if not crud_user.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
        
        # Create new refresh token
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = security.create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
        
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> UserResponse:
    """
    Get current user information
    """
    return current_user


@router.post("/logout")
def logout(
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Logout current user (in a real implementation, you might want to blacklist the token)
    """
    return {"message": "Successfully logged out"}