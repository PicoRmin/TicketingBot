"""
Dependencies for API endpoints
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.models import User
from app.core.security import decode_access_token
from app.schemas.token import TokenData
from app.core.enums import UserRole

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from token
    
    Args:
        token: JWT token from request
        db: Database session
        
    Returns:
        User: Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(
            username=username,
            user_id=payload.get("user_id"),
            role=payload.get("role"),
            branch_id=payload.get("branch_id"),
        )
    except JWTError:
        raise credentials_exception
    
    user_query = db.query(User)
    if token_data.user_id:
        user = user_query.filter(User.id == token_data.user_id).first()
    else:
        user = user_query.filter(User.username == token_data.username).first()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_roles(*allowed_roles: UserRole):
    allowed_set = set(allowed_roles)

    async def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user

    return dependency


require_admin = require_roles(UserRole.ADMIN, UserRole.CENTRAL_ADMIN)
require_central_admin = require_roles(UserRole.CENTRAL_ADMIN)
require_branch_admin = require_roles(UserRole.BRANCH_ADMIN, UserRole.CENTRAL_ADMIN)
require_report_access = require_roles(UserRole.REPORT_MANAGER, UserRole.ADMIN, UserRole.CENTRAL_ADMIN)

