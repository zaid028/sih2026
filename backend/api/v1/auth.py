"""
FIREGUARD AI - Authentication API (Requirement 19)
JWT token issuing, verification, registration, and user profiles with RBAC.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.entities import User
from backend.schemas.pydantic_models import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfileResponse
)
from backend.utils.security import hash_password, verify_password, create_access_token, decode_access_token
from backend.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

@router.post("/register", response_model=UserProfileResponse, status_code=201, summary="Register a new user")
def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.username == req.username) | (User.email == req.email)).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail={"code": "USER_EXISTS", "message": "Username or email is already registered"}
        )

    user = User(
        id=str(uuid.uuid4()),
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
        role=req.role or "OPERATOR",
        full_name=req.full_name,
        agency=req.agency or "",
        phone=req.phone or ""
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.to_dict()

@router.post("/login", response_model=TokenResponse, summary="Log in with username and password to obtain JWT")
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid username or password"}
        )

    token = create_access_token({"sub": user.username, "role": user.role, "uid": user.id})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        username=user.username,
        user_id=user.id,
        expires_in=86400
    )

@router.post("/refresh", response_model=TokenResponse, summary="Refresh existing JWT access token")
def refresh_token(
    authorization: str = Header(..., description="Current Bearer JWT"),
    db: Session = Depends(get_db)
):
    try:
        scheme, token = authorization.split()
        payload = decode_access_token(token)
        if not payload or "sub" not in payload:
            raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Token expired or invalid"})

        user = db.query(User).filter(User.username == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=401, detail={"code": "USER_NOT_FOUND", "message": "User no longer exists"})

        new_token = create_access_token({"sub": user.username, "role": user.role, "uid": user.id})
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            role=user.role,
            username=user.username,
            user_id=user.id,
            expires_in=86400
        )
    except Exception:
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Invalid authorization header"})

@router.get("/me", response_model=UserProfileResponse, summary="Get currently authenticated user profile")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()
