"""
FIREGUARD AI - Authentication and Role-Based Access Control (RBAC)
Implements JWT tokens, password hashing with salt, and role decorators.
Roles: admin, operator, facility_manager, analyst, public
"""
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jwt
from app.config import Config

class AuthService:
    ROLES = ["admin", "operator", "facility_manager", "analyst", "public"]

    @staticmethod
    def hash_password(password: str, salt: str = None) -> str:
        """Hash a password with salt using SHA-256."""
        if not salt:
            salt = os.urandom(16).hex()
        digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        return f"{salt}${digest}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify password against stored salt$digest."""
        try:
            salt, digest = stored_hash.split("$", 1)
            check = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
            return check == digest
        except Exception:
            return False

    @staticmethod
    def create_token(user_id: int, username: str, role: str) -> str:
        """Create a signed JWT token."""
        payload = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token."""
        try:
            return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except Exception:
            return None
