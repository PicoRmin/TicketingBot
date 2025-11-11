"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas.user import LoginRequest, UserResponse
from app.schemas.token import Token
from app.core.security import verify_password, create_access_token
from app.core.enums import UserRole
from app.api.deps import get_current_active_user
from app.config import settings
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint - OAuth2 compatible
    
    Args:
        form_data: OAuth2 password request form (username, password)
        db: Database session
        
    Returns:
        Token: Access token and token type
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        lang = resolve_lang(request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translate("auth.login_failed", lang),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        lang = resolve_lang(request, user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translate("auth.login_failed", resolve_lang(request, user)),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        lang = resolve_lang(request, user)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("auth.inactive_user", lang)
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login-form", response_model=Token)
async def login_form(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint - JSON form data
    
    Args:
        login_data: Login request (username, password)
        db: Database session
        
    Returns:
        Token: Access token and token type
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user:
        lang = resolve_lang(request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translate("auth.login_failed", lang),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        lang = resolve_lang(request, user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translate("auth.login_failed", lang),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        lang = resolve_lang(request, user)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("auth.inactive_user", lang)
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user information
    """
    return current_user

