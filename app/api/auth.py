"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas.user import LoginRequest, UserResponse, TelegramLinkRequest
from app.schemas.token import Token, RefreshTokenRequest
from app.core.security import verify_password, create_access_token
from app.core.enums import UserRole
from app.api.deps import get_current_active_user
from app.config import settings
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang
from app.services.refresh_token_service import (
    issue_refresh_token,
    verify_refresh_token,
    rotate_refresh_token,
    revoke_refresh_token,
)

router = APIRouter()


def _build_access_payload(user: User) -> dict:
    return {
        "sub": user.username,
        "user_id": user.id,
        "role": user.role.value,
        "branch_id": user.branch_id,
    }


def _create_token_pair(user: User, request: Request, db: Session) -> Token:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=_build_access_payload(user),
        expires_delta=access_token_expires,
    )
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    refresh_token, _ = issue_refresh_token(
        db,
        user,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


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
    
    # Create access & refresh tokens
    token_pair = _create_token_pair(user, request, db)
    
    return token_pair


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
    token_pair = _create_token_pair(user, request, db)
    
    return token_pair


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


@router.post("/link-telegram", response_model=UserResponse)
async def link_telegram_account(
    data: TelegramLinkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Link current authenticated user with their Telegram chat id."""
    # Ensure chat_id stored as string
    chat_id_str = str(data.chat_id)

    # Clear previous association if another user uses same chat id
    existing = (
        db.query(User)
        .filter(User.telegram_chat_id == chat_id_str, User.id != current_user.id)
        .first()
    )
    if existing:
        existing.telegram_chat_id = None

    current_user.telegram_chat_id = chat_id_str
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: Request,
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    record = verify_refresh_token(db, data.refresh_token)
    if not record or not record.user or not record.user.is_active:
        lang = resolve_lang(request, record.user if record else None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=translate("auth.invalid_refresh", lang),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = record.user
    new_refresh_token, _ = rotate_refresh_token(
        db,
        record,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=_build_access_payload(user),
        expires_delta=access_token_expires,
    )

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    record = verify_refresh_token(db, data.refresh_token)
    if record:
        revoke_refresh_token(db, record)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

