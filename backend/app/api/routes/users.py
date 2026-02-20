import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_connection_repo, get_user_service
from app.api.schemas import ConnectionResponse, NetworkResponse, UserCreate, UserResponse
from app.core.entities import User
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(
    svc: UserService = Depends(get_user_service), conn_repo=Depends(get_connection_repo)
):
    users = svc.get_all()
    result = []
    for u in users:
        conns = conn_repo.get_connections(u.id)
        result.append(
            UserResponse(
                id=u.id,
                name=u.name,
                bio=u.bio,
                skills=u.skills,
                interests=u.interests,
                open_to=u.open_to,
                created_at=u.created_at,
                connection_count=len(conns),
            )
        )
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
    return UserResponse(
        id=user.id,
        name=user.name,
        bio=user.bio,
        skills=user.skills,
        interests=user.interests,
        open_to=user.open_to,
        created_at=user.created_at,
        connection_count=len(conns),
    )


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
    return UserResponse(
        id=created.id,
        name=created.name,
        bio=created.bio,
        skills=created.skills,
        interests=created.interests,
        open_to=created.open_to,
        created_at=created.created_at,
    )


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

    all_conns = conn_repo.get_connections(user_id)
    return NetworkResponse(
        user=UserResponse(
            id=user.id,
            name=user.name,
            bio=user.bio,
            skills=user.skills,
            interests=user.interests,
            open_to=user.open_to,
            created_at=user.created_at,
            connection_count=len(all_conns),
        ),
        connections=connections,
    )
