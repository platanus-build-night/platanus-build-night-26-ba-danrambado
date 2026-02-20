import json
from typing import Optional

from sqlalchemy.orm import Session

from app.adapters.persistence.models import UserModel
from app.core.entities import User
from app.ports.repositories import UserRepository


class SqlUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            name=model.name,
            bio=model.bio,
            skills=json.loads(model.skills),
            interests=json.loads(model.interests),
            open_to=json.loads(model.open_to),
            email=model.email or "",
            password_hash=model.password_hash or "",
            created_at=model.created_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            password_hash=entity.password_hash,
            bio=entity.bio,
            skills=json.dumps(entity.skills),
            interests=json.dumps(entity.interests),
            open_to=json.dumps(entity.open_to),
            created_at=entity.created_at,
        )

    def get_all(self) -> list[User]:
        models = self._session.query(UserModel).order_by(UserModel.created_at).all()
        return [self._to_entity(m) for m in models]

    def get_by_id(self, user_id: str) -> Optional[User]:
        model = self._session.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> Optional[User]:
        model = self._session.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None

    def create(self, user: User) -> User:
        model = self._to_model(user)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)
