from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.adapters.ai.anthropic_adapter import AnthropicAdapter
from app.adapters.embeddings.chroma_adapter import ChromaEmbeddingAdapter
from app.adapters.persistence.connection_repo import SqlConnectionRepository
from app.adapters.persistence.database import get_session
from app.adapters.persistence.match_repo import SqlMatchRepository
from app.adapters.persistence.opportunity_repo import SqlOpportunityRepository
from app.adapters.persistence.user_repo import SqlUserRepository
from app.ports.ai_port import AIPort
from app.ports.embedding_port import EmbeddingPort
from app.services.matching_service import MatchingService
from app.services.opportunity_service import OpportunityService
from app.services.user_service import UserService


@lru_cache
def get_embedding() -> EmbeddingPort:
    return ChromaEmbeddingAdapter()


@lru_cache
def get_ai() -> AIPort:
    return AnthropicAdapter()


def get_user_service(
    session: Session = Depends(get_session),
    embedding: EmbeddingPort = Depends(get_embedding),
) -> UserService:
    return UserService(SqlUserRepository(session), embedding)


def get_opportunity_service(
    session: Session = Depends(get_session),
) -> OpportunityService:
    return OpportunityService(SqlOpportunityRepository(session))


def get_matching_service(
    session: Session = Depends(get_session),
    embedding: EmbeddingPort = Depends(get_embedding),
    ai: AIPort = Depends(get_ai),
) -> MatchingService:
    return MatchingService(
        user_repo=SqlUserRepository(session),
        match_repo=SqlMatchRepository(session),
        connection_repo=SqlConnectionRepository(session),
        embedding=embedding,
        ai=ai,
    )


def get_connection_repo(session: Session = Depends(get_session)):
    return SqlConnectionRepository(session)


def get_user_repo(session: Session = Depends(get_session)):
    return SqlUserRepository(session)
