from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import user as crud_user
from app.crud import audit as crud_audit
from app.crud import token as crud_token
from app.models.user import User
from app.schemas.user import Token, UserResponse, UserCreate

router = APIRouter()


@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Lockout check
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if user and user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account locked. Try again later.")
    # Authenticate
    user = crud_user.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        # Record failed attempt
        u = crud_user.get_user_by_email(db, email=form_data.username)
        if u:
            from datetime import timedelta as td
            u.failed_login_attempts = (u.failed_login_attempts or 0) + 1
            # Lock account for 5 minutes after 5 failures
            if u.failed_login_attempts >= 5:
                u.locked_until = datetime.utcnow() + td(minutes=5)
                u.failed_login_attempts = 0
            db.commit()
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
    user.last_login = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = security.create_refresh_token(
        user.id, expires_delta=refresh_token_expires
    )
    # Persist refresh token
    crud_token.create_refresh_token(db, user_id=user.id, token=refresh_token, expires_at=datetime.utcnow() + refresh_token_expires)
    # Audit
    crud_audit.log_action(db, user_id=user.id, action="login", target=None, metadata=None)
    
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
        
        # Check token exists in DB and not expired
        db_token = crud_token.get_refresh_token(db, token=refresh_token)
        if not db_token or db_token.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
        # Rotate refresh token
        crud_token.delete_refresh_token(db, token=refresh_token)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = security.create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        )
        crud_token.create_refresh_token(db, user_id=user.id, token=new_refresh_token, expires_at=datetime.utcnow() + refresh_token_expires)
        
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


@router.post("/register", response_model=UserResponse)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> UserResponse:
    if crud_user.get_user_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_in.username and crud_user.get_user_by_username(db, username=user_in.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    user = crud_user.create_user(db, user=user_in)
    crud_audit.log_action(db, user_id=user.id, action="register", target=None, metadata=None)
    return user


@router.post("/logout")
def logout(
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Logout current user (in a real implementation, you might want to blacklist the token)
    """
    return {"message": "Successfully logged out"}