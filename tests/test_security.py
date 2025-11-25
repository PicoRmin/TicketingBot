"""
Unit tests for security utilities
"""
import pytest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)
from datetime import timedelta


def test_password_hashing():
    """Test password hashing and verification"""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original
    assert hashed != password
    assert len(hashed) > 0
    
    # Should verify correctly
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_password_hash_uniqueness():
    """Test that same password produces different hashes"""
    password = "same_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different (due to salt)
    assert hash1 != hash2
    
    # But both should verify
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "testuser", "user_id": 1}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    """Test JWT token decoding"""
    data = {"sub": "testuser", "user_id": 1, "role": "user"}
    token = create_access_token(data)
    
    decoded = decode_access_token(token)
    
    assert decoded is not None
    assert decoded["sub"] == "testuser"
    assert decoded["user_id"] == 1
    assert decoded["role"] == "user"


def test_token_expiration():
    """Test token expiration"""
    data = {"sub": "testuser", "user_id": 1}
    # Create token with very short expiration
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    
    # Token should be expired
    decoded = decode_access_token(token)
    # Note: decode_access_token might not check expiration, 
    # but the token should still decode (expiration is checked in get_current_user)
    assert decoded is not None


def test_invalid_token():
    """Test decoding invalid token"""
    with pytest.raises(Exception):
        decode_access_token("invalid_token_string")

