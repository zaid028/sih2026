"""
FIREGUARD AI - Security & Authentication Utilities
Password hashing (SHA-256 with salt) and JWT token generation / verification.
"""
import hashlib
import hmac
import time
from typing import Optional, Dict, Any
import jwt
from backend.config.settings import settings

SALT = "fireguard_tactical_sih2026_salt_secure"

def hash_password(password: str) -> str:
    """Hash password using SHA-256 and fixed salt."""
    salted = f"{password}{SALT}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password matches hash."""
    return hmac.compare_digest(hash_password(plain_password), hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta_seconds: Optional[int] = None) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()
    expire_time = time.time() + (expires_delta_seconds if expires_delta_seconds else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    to_encode.update({"exp": expire_time})
    return jwt.encode(to_encode, settings.effective_jwt_secret, algorithm="HS256")

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a signed JWT token."""
    try:
        payload = jwt.decode(token, settings.effective_jwt_secret, algorithms=["HS256"])
        return payload
    except Exception:
        return None
