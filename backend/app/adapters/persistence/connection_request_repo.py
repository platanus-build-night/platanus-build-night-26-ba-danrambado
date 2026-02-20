from typing import Optional

from sqlalchemy.orm import Session

from app.adapters.persistence.models import ConnectionRequestModel
from app.core.entities import ConnectionRequest
from app.ports.repositories import ConnectionRequestRepository


class SqlConnectionRequestRepository(ConnectionRequestRepository):
    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: ConnectionRequestModel) -> ConnectionRequest:
        return ConnectionRequest(
            id=model.id,
            from_user_id=model.from_user_id,
            to_user_id=model.to_user_id,
            opportunity_id=model.opportunity_id,
            match_id=model.match_id,
            status=model.status,
            created_at=model.created_at,
        )

    def create(self, req: ConnectionRequest) -> ConnectionRequest:
        model = ConnectionRequestModel(
            id=req.id,
            from_user_id=req.from_user_id,
            to_user_id=req.to_user_id,
            opportunity_id=req.opportunity_id,
            match_id=req.match_id,
            status=req.status,
            created_at=req.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, request_id: str) -> Optional[ConnectionRequest]:
        model = (
            self._session.query(ConnectionRequestModel)
            .filter(ConnectionRequestModel.id == request_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def get_incoming(self, user_id: str) -> list[ConnectionRequest]:
        models = (
            self._session.query(ConnectionRequestModel)
            .filter(
                ConnectionRequestModel.to_user_id == user_id,
                ConnectionRequestModel.status == "pending",
            )
            .order_by(ConnectionRequestModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def get_outgoing(self, user_id: str) -> list[ConnectionRequest]:
        models = (
            self._session.query(ConnectionRequestModel)
            .filter(ConnectionRequestModel.from_user_id == user_id)
            .order_by(ConnectionRequestModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def update_status(self, request_id: str, status: str) -> Optional[ConnectionRequest]:
        model = (
            self._session.query(ConnectionRequestModel)
            .filter(ConnectionRequestModel.id == request_id)
            .first()
        )
        if not model:
            return None
        model.status = status
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def exists(self, from_user_id: str, to_user_id: str, opportunity_id: str) -> bool:
        count = (
            self._session.query(ConnectionRequestModel)
            .filter(
                ConnectionRequestModel.from_user_id == from_user_id,
                ConnectionRequestModel.to_user_id == to_user_id,
                ConnectionRequestModel.opportunity_id == opportunity_id,
            )
            .count()
        )
        return count > 0
