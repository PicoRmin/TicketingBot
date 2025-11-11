"""
Security utilities for password hashing and token management
"""
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash using bcrypt
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password (bcrypt format)
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        # Ensure inputs are strings
        if not isinstance(plain_password, str):
            plain_password = str(plain_password)
        if not isinstance(hashed_password, str):
            hashed_password = str(hashed_password)
        
        # Encode to bytes
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        
        # Verify using bcrypt
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        # Log error in production (optional)
        # logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: The plain text password
        
    Returns:
        str: The hashed password
    """
    # Ensure password is a string
    if not isinstance(password, str):
        password = str(password)
    
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode a JWT access token
    
    Args:
        token: The JWT token to decode
        
    Returns:
        dict: The decoded token data
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise e

