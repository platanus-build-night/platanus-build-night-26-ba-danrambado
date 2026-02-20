from sqlalchemy.orm import Session

from app.adapters.persistence.models import FeedbackModel
from app.core.entities import Feedback
from app.ports.repositories import FeedbackRepository


class SqlFeedbackRepository(FeedbackRepository):
    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: FeedbackModel) -> Feedback:
        return Feedback(
            id=model.id,
            from_user_id=model.from_user_id,
            to_user_id=model.to_user_id,
            opportunity_type=model.opportunity_type,
            text=model.text,
            created_at=model.created_at,
        )

    def get_by_user(self, to_user_id: str) -> list[Feedback]:
        models = (
            self._session.query(FeedbackModel)
            .filter(FeedbackModel.to_user_id == to_user_id)
            .order_by(FeedbackModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def create(self, feedback: Feedback) -> Feedback:
        model = FeedbackModel(
            id=feedback.id,
            from_user_id=feedback.from_user_id,
            to_user_id=feedback.to_user_id,
            opportunity_type=feedback.opportunity_type,
            text=feedback.text,
            created_at=feedback.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def has_feedback(self, from_user_id: str, to_user_id: str, opportunity_type: str) -> bool:
        count = (
            self._session.query(FeedbackModel)
            .filter(
                FeedbackModel.from_user_id == from_user_id,
                FeedbackModel.to_user_id == to_user_id,
                FeedbackModel.opportunity_type == opportunity_type,
            )
            .count()
        )
        return count > 0
