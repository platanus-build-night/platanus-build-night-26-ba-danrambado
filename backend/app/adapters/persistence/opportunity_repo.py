from typing import Optional

from sqlalchemy.orm import Session

from app.adapters.persistence.models import OpportunityModel
from app.core.entities import Opportunity
from app.core.enums import OpportunityType
from app.ports.repositories import OpportunityRepository


class SqlOpportunityRepository(OpportunityRepository):
    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: OpportunityModel) -> Opportunity:
        return Opportunity(
            id=model.id,
            title=model.title,
            description=model.description,
            type=OpportunityType(model.type),
            posted_by=model.posted_by,
            created_at=model.created_at,
        )

    def _to_model(self, entity: Opportunity) -> OpportunityModel:
        return OpportunityModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            type=entity.type.value,
            posted_by=entity.posted_by,
            created_at=entity.created_at,
        )

    def get_all(self) -> list[Opportunity]:
        models = (
            self._session.query(OpportunityModel).order_by(OpportunityModel.created_at.desc()).all()
        )
        return [self._to_entity(m) for m in models]

    def get_by_id(self, opportunity_id: str) -> Optional[Opportunity]:
        model = (
            self._session.query(OpportunityModel)
            .filter(OpportunityModel.id == opportunity_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def create(self, opportunity: Opportunity) -> Opportunity:
        model = self._to_model(opportunity)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)
