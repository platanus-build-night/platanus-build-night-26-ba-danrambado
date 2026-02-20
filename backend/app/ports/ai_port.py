from abc import ABC, abstractmethod

from app.core.entities import CandidateScore, Opportunity, RankedMatch


class AIPort(ABC):
    @abstractmethod
    async def rank_and_explain(
        self,
        opportunity: Opportunity,
        candidates: list[CandidateScore],
    ) -> list[RankedMatch]:
        """
        Given an opportunity and pre-filtered candidates (from Phase 1),
        rank them and produce a short explanation for each match.
        """
        ...
