import uuid
from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, Header, HTTPException

from app.api.dependencies import get_current_user, get_session_repo, get_user_service
from app.api.schemas import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.core.entities import User
from app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(
    body: RegisterRequest,
    svc: UserService = Depends(get_user_service),
    session_repo=Depends(get_session_repo),
):
    existing = svc._repo.get_by_email(body.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        name=body.name,
        email=body.email,
        password_hash=_hash_password(body.password),
        bio=body.bio,
        skills=body.skills,
        interests=body.interests,
        open_to=body.open_to,
    )
    created = svc.create(user)

    token = str(uuid.uuid4())
    session_repo.create(token, created.id)

    return AuthResponse(
        token=token,
        user=UserResponse(
            id=created.id,
            name=created.name,
            email=created.email,
            bio=created.bio,
            skills=created.skills,
            interests=created.interests,
            open_to=created.open_to,
            created_at=created.created_at,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(
    body: LoginRequest,
    svc: UserService = Depends(get_user_service),
    session_repo=Depends(get_session_repo),
):
    user = svc._repo.get_by_email(body.email)
    if not user or not _check_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = str(uuid.uuid4())
    session_repo.create(token, user.id)

    return AuthResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            bio=user.bio,
            skills=user.skills,
            interests=user.interests,
            open_to=user.open_to,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        bio=current_user.bio,
        skills=current_user.skills,
        interests=current_user.interests,
        open_to=current_user.open_to,
        created_at=current_user.created_at,
    )


@router.post("/logout", status_code=204)
def logout(
    current_user: User = Depends(get_current_user),
    session_repo=Depends(get_session_repo),
    authorization: Optional[str] = Header(None),
):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        session_repo.delete(token)
