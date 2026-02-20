from app.core.entities import Opportunity
from app.ports.repositories import OpportunityRepository


class OpportunityService:
    def __init__(self, repo: OpportunityRepository):
        self._repo = repo

    def get_all(self) -> list[Opportunity]:
        return self._repo.get_all()

    def get_by_id(self, opportunity_id: str) -> Opportunity | None:
        return self._repo.get_by_id(opportunity_id)

    def create(self, opportunity: Opportunity) -> Opportunity:
        return self._repo.create(opportunity)
