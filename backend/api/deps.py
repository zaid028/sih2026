"""
FIREGUARD AI - FastAPI Dependency Injection & RBAC Security Guard
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.entities import User
from backend.utils.security import decode_access_token

def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Extract current user from Bearer JWT token if provided."""
    if not authorization:
        return None
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        payload = decode_access_token(token)
        if not payload or "sub" not in payload:
            return None
        user = db.query(User).filter(User.username == payload["sub"]).first()
        return user
    except Exception:
        return None

def get_current_user(
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Enforce authentication on protected endpoints."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Authentication token missing or invalid"}
        )
    return current_user

def require_roles(allowed_roles: List[str]):
    """Enforce role-based access control."""
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": f"Action requires one of roles: {allowed_roles}"}
            )
        return user
    return role_checker
