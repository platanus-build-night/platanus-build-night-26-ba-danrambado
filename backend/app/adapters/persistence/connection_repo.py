from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.adapters.persistence.models import ConnectionModel, UserModel
from app.core.entities import Connection
from app.core.enums import ConnectionSource
from app.ports.repositories import ConnectionRepository


class SqlConnectionRepository(ConnectionRepository):
    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: ConnectionModel) -> Connection:
        return Connection(
            id=model.id,
            user_a=model.user_a,
            user_b=model.user_b,
            source=ConnectionSource(model.source),
            strength=model.strength,
            created_at=model.created_at,
        )

    def get_connections(self, user_id: str) -> list[Connection]:
        models = (
            self._session.query(ConnectionModel)
            .filter(
                or_(
                    ConnectionModel.user_a == user_id,
                    ConnectionModel.user_b == user_id,
                )
            )
            .all()
        )
        return [self._to_entity(m) for m in models]

    def get_second_degree(self, user_id: str) -> dict[str, list[str]]:
        first_degree_conns = self.get_connections(user_id)
        first_degree_ids = set()
        for c in first_degree_conns:
            other = c.user_b if c.user_a == user_id else c.user_a
            first_degree_ids.add(other)

        second_degree: dict[str, list[str]] = {}
        for fid in first_degree_ids:
            friend_name = self._session.query(UserModel.name).filter(UserModel.id == fid).scalar()
            their_conns = self.get_connections(fid)
            for c in their_conns:
                other = c.user_b if c.user_a == fid else c.user_a
                if other == user_id or other in first_degree_ids:
                    continue
                if other not in second_degree:
                    second_degree[other] = []
                if friend_name and friend_name not in second_degree[other]:
                    second_degree[other].append(friend_name)

        return second_degree

    def create(self, connection: Connection) -> Connection:
        model = ConnectionModel(
            id=connection.id,
            user_a=connection.user_a,
            user_b=connection.user_b,
            source=connection.source.value,
            strength=connection.strength,
            created_at=connection.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def create_batch(self, connections: list[Connection]) -> list[Connection]:
        models = []
        for c in connections:
            model = ConnectionModel(
                id=c.id,
                user_a=c.user_a,
                user_b=c.user_b,
                source=c.source.value,
                strength=c.strength,
                created_at=c.created_at,
            )
            self._session.add(model)
            models.append(model)
        self._session.commit()
        for model in models:
            self._session.refresh(model)
        return [self._to_entity(m) for m in models]
