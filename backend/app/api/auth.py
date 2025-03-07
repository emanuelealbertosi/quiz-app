from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_password,
    get_current_active_user,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserResponse, UserDetailResponse

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    print(f"Login attempt for user: {form_data.username}")
    
    # Log all users in the database for debugging
    all_users = db.query(User).all()
    print(f"All users in database: {[u.username for u in all_users]}")
    
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        print(f"User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"User found: {user.username}, checking password")
    if not verify_password(form_data.password, user.hashed_password):
        print(f"Password verification failed for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        print(f"User is inactive: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    print(f"Login successful for user: {user.username}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(user.id, expires_delta=access_token_expires)
    print(f"Token created: {token[:10]}...")
    
    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.post("/logout")
def logout() -> Any:
    """
    Logout a user (client-side only, token is still valid until it expires)
    """
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserDetailResponse)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user information
    """
    return current_user
