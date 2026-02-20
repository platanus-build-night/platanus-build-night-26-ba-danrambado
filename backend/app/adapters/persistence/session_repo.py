from typing import Optional

from sqlalchemy.orm import Session

from app.adapters.persistence.models import SessionModel
from app.ports.repositories import SessionRepository


class SqlSessionRepository(SessionRepository):
    def __init__(self, session: Session):
        self._session = session

    def create(self, session_id: str, user_id: str) -> None:
        model = SessionModel(id=session_id, user_id=user_id)
        self._session.add(model)
        self._session.commit()

    def get_user_id(self, session_id: str) -> Optional[str]:
        model = (
            self._session.query(SessionModel)
            .filter(SessionModel.id == session_id)
            .first()
        )
        return model.user_id if model else None

    def delete(self, session_id: str) -> None:
        self._session.query(SessionModel).filter(SessionModel.id == session_id).delete()
        self._session.commit()
