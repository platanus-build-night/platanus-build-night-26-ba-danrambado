from sqlalchemy.orm import Session

from app.adapters.persistence.models import MatchModel
from app.core.entities import Match
from app.ports.repositories import MatchRepository


class SqlMatchRepository(MatchRepository):
    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: MatchModel) -> Match:
        return Match(
            id=model.id,
            opportunity_id=model.opportunity_id,
            user_id=model.user_id,
            score=model.score,
            embedding_score=model.embedding_score,
            network_score=model.network_score,
            explanation=model.explanation,
            rank=model.rank,
            created_at=model.created_at,
        )

    def get_by_opportunity(self, opportunity_id: str) -> list[Match]:
        models = (
            self._session.query(MatchModel)
            .filter(MatchModel.opportunity_id == opportunity_id)
            .order_by(MatchModel.rank)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def create_batch(self, matches: list[Match]) -> list[Match]:
        models = []
        for m in matches:
            model = MatchModel(
                id=m.id,
                opportunity_id=m.opportunity_id,
                user_id=m.user_id,
                score=m.score,
                embedding_score=m.embedding_score,
                network_score=m.network_score,
                explanation=m.explanation,
                rank=m.rank,
                created_at=m.created_at,
            )
            self._session.add(model)
            models.append(model)
        self._session.commit()
        for model in models:
            self._session.refresh(model)
        return [self._to_entity(model) for model in models]
