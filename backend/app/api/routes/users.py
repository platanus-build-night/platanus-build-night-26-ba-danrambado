import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_connection_repo,
    get_connection_request_repo,
    get_current_user,
    get_user_service,
)
from app.api.schemas import (
    ConnectionResponse,
    LayeredNetworkResponse,
    NetworkMemberResponse,
    NetworkResponse,
    SearchResultResponse,
    UserCreate,
    UserResponse,
)
from app.adapters.persistence.database import get_session
from app.adapters.persistence.models import UserModel
from app.core.entities import User
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


def _user_response(user: User, conn_count: int = 0) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        bio=user.bio,
        skills=user.skills,
        interests=user.interests,
        open_to=user.open_to,
        created_at=user.created_at,
        connection_count=conn_count,
    )


@router.get("/search", response_model=list[SearchResultResponse])
def search_users(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_user_service),
    conn_repo=Depends(get_connection_repo),
    session: Session = Depends(get_session),
):
    term = f"%{q.lower()}%"
    models = (
        session.query(UserModel)
        .filter(
            (UserModel.name.ilike(term))
            | (UserModel.skills.ilike(term))
            | (UserModel.interests.ilike(term))
            | (UserModel.bio.ilike(term))
        )
        .limit(20)
        .all()
    )

    first_degree_ids = set()
    conns = conn_repo.get_connections(current_user.id)
    for c in conns:
        other = c.user_b if c.user_a == current_user.id else c.user_a
        first_degree_ids.add(other)

    second_degree = conn_repo.get_second_degree(current_user.id)

    results = []
    for m in models:
        if m.id == current_user.id:
            continue
        user_conns = conn_repo.get_connections(m.id)
        user = User(
            id=m.id, name=m.name, bio=m.bio,
            skills=json.loads(m.skills), interests=json.loads(m.interests),
            open_to=json.loads(m.open_to), email=m.email or "",
            password_hash="", created_at=m.created_at,
        )
        degree = "other"
        shared: list[str] = []
        if m.id in first_degree_ids:
            degree = "1st"
        elif m.id in second_degree:
            degree = "2nd"
            shared = second_degree[m.id]

        results.append(SearchResultResponse(
            user=_user_response(user, len(user_conns)),
            degree=degree,
            shared_connections=shared,
        ))
    return results


@router.get("/network/me", response_model=LayeredNetworkResponse)
def get_my_network(
    current_user: User = Depends(get_current_user),
    svc: UserService = Depends(get_user_service),
    conn_repo=Depends(get_connection_repo),
    req_repo=Depends(get_connection_request_repo),
):
    conns = conn_repo.get_connections(current_user.id)
    first_degree: list[NetworkMemberResponse] = []
    first_degree_ids: set[str] = set()

    for c in conns:
        other_id = c.user_b if c.user_a == current_user.id else c.user_a
        if other_id in first_degree_ids:
            continue
        first_degree_ids.add(other_id)
        other = svc.get_by_id(other_id)
        if other:
            other_conns = conn_repo.get_connections(other_id)
            first_degree.append(NetworkMemberResponse(
                user=_user_response(other, len(other_conns)),
                degree=1,
                connection_source=c.source.value,
            ))

    second_degree_map = conn_repo.get_second_degree(current_user.id)
    second_degree: list[NetworkMemberResponse] = []
    for uid, shared in second_degree_map.items():
        other = svc.get_by_id(uid)
        if other:
            other_conns = conn_repo.get_connections(uid)
            second_degree.append(NetworkMemberResponse(
                user=_user_response(other, len(other_conns)),
                degree=2,
                shared_connections=shared,
            ))

    pending = len(req_repo.get_incoming(current_user.id))

    return LayeredNetworkResponse(
        first_degree=first_degree,
        second_degree=second_degree,
        pending_incoming=pending,
    )


@router.get("", response_model=list[UserResponse])
def list_users(
    svc: UserService = Depends(get_user_service), conn_repo=Depends(get_connection_repo)
):
    users = svc.get_all()
    result = []
    for u in users:
        conns = conn_repo.get_connections(u.id)
        result.append(_user_response(u, len(conns)))
    return result


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    svc: UserService = Depends(get_user_service),
    conn_repo=Depends(get_connection_repo),
):
    user = svc.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    conns = conn_repo.get_connections(user.id)
    return _user_response(user, len(conns))


@router.post("", response_model=UserResponse, status_code=201)
def create_user(body: UserCreate, svc: UserService = Depends(get_user_service)):
    user = User(
        id=str(uuid.uuid4()),
        name=body.name,
        bio=body.bio,
        skills=body.skills,
        interests=body.interests,
        open_to=body.open_to,
    )
    created = svc.create(user)
    return _user_response(created)


@router.get("/{user_id}/network", response_model=NetworkResponse)
def get_network(
    user_id: str,
    svc: UserService = Depends(get_user_service),
    conn_repo=Depends(get_connection_repo),
):
    user = svc.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    conns = conn_repo.get_connections(user_id)
    connections = []
    for c in conns:
        other_id = c.user_b if c.user_a == user_id else c.user_a
        other = svc.get_by_id(other_id)
        if other:
            connections.append(
                ConnectionResponse(
                    id=c.id,
                    user_id=other.id,
                    user_name=other.name,
                    source=c.source.value,
                    strength=c.strength,
                )
            )

    return NetworkResponse(
        user=_user_response(user, len(conns)),
        connections=connections,
    )
