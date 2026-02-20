import uuid
from datetime import datetime

from app.core.entities import CandidateScore, Match, Opportunity, User
from app.ports.ai_port import AIPort
from app.ports.embedding_port import EmbeddingPort
from app.ports.repositories import (
    ConnectionRepository,
    MatchRepository,
    UserRepository,
)

FIRST_DEGREE_BOOST = 0.15
SECOND_DEGREE_BOOST = 0.08


class MatchingService:
    def __init__(
        self,
        user_repo: UserRepository,
        match_repo: MatchRepository,
        connection_repo: ConnectionRepository,
        embedding: EmbeddingPort,
        ai: AIPort,
    ):
        self._user_repo = user_repo
        self._match_repo = match_repo
        self._connection_repo = connection_repo
        self._embedding = embedding
        self._ai = ai

    async def find_matches(self, opportunity: Opportunity, top_k: int = 5) -> list[Match]:
        candidates = self._phase1_retrieval(opportunity, top_k)
        if not candidates:
            return []

        ranked = await self._phase2_explain(opportunity, candidates)

        matches = []
        for r in ranked:
            candidate = next((c for c in candidates if c.user.id == r.user_id), None)
            if not candidate:
                continue
            matches.append(
                Match(
                    id=str(uuid.uuid4()),
                    opportunity_id=opportunity.id,
                    user_id=r.user_id,
                    score=r.score,
                    embedding_score=candidate.embedding_score,
                    network_score=candidate.network_score,
                    explanation=r.explanation,
                    rank=r.rank,
                    created_at=datetime.utcnow(),
                )
            )

        self._match_repo.create_batch(matches)
        return matches

    def _phase1_retrieval(self, opportunity: Opportunity, top_k: int) -> list[CandidateScore]:
        query_text = f"{opportunity.title}. {opportunity.description}"
        raw_results = self._embedding.search_similar(query_text, n_results=top_k * 3)

        first_degree_ids = set()
        connections = self._connection_repo.get_connections(opportunity.posted_by)
        for c in connections:
            other = c.user_b if c.user_a == opportunity.posted_by else c.user_a
            first_degree_ids.add(other)

        second_degree = self._connection_repo.get_second_degree(opportunity.posted_by)

        opp_type = opportunity.type.value
        users_cache: dict[str, User] = {}

        candidates: list[CandidateScore] = []
        for result in raw_results:
            uid = result["user_id"]
            if uid == opportunity.posted_by:
                continue

            user = self._user_repo.get_by_id(uid)
            if not user:
                continue
            users_cache[uid] = user

            if opp_type not in user.open_to:
                continue

            embedding_score = max(0.0, min(1.0, result["score"]))

            network_score = 0.0
            shared_connections: list[str] = []
            if uid in first_degree_ids:
                network_score = FIRST_DEGREE_BOOST
                for conn in connections:
                    other = conn.user_b if conn.user_a == opportunity.posted_by else conn.user_a
                    if other == uid:
                        poster = self._user_repo.get_by_id(opportunity.posted_by)
                        if poster:
                            shared_connections.append("Direct connection")
                        break
            elif uid in second_degree:
                network_score = SECOND_DEGREE_BOOST
                shared_connections = second_degree[uid]

            combined = embedding_score + network_score

            candidates.append(
                CandidateScore(
                    user=user,
                    embedding_score=embedding_score,
                    network_score=network_score,
                    combined_score=combined,
                    shared_connections=shared_connections,
                )
            )

        candidates.sort(key=lambda c: c.combined_score, reverse=True)
        return candidates[:top_k]

    async def _phase2_explain(self, opportunity: Opportunity, candidates: list[CandidateScore]):
        return await self._ai.rank_and_explain(opportunity, candidates)

    def get_matches(self, opportunity_id: str) -> list[Match]:
        return self._match_repo.get_by_opportunity(opportunity_id)
