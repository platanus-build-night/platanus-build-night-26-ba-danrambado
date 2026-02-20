from functools import lru_cache
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.adapters.ai.anthropic_adapter import AnthropicAdapter
from app.adapters.embeddings.chroma_adapter import ChromaEmbeddingAdapter
from app.adapters.persistence.connection_repo import SqlConnectionRepository
from app.adapters.persistence.database import get_session
from app.adapters.persistence.feedback_repo import SqlFeedbackRepository
from app.adapters.persistence.match_repo import SqlMatchRepository
from app.adapters.persistence.opportunity_repo import SqlOpportunityRepository
from app.adapters.persistence.session_repo import SqlSessionRepository
from app.adapters.persistence.user_repo import SqlUserRepository
from app.core.entities import User
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


def get_session_repo(session: Session = Depends(get_session)):
    return SqlSessionRepository(session)


def get_feedback_repo(session: Session = Depends(get_session)):
    return SqlFeedbackRepository(session)


def get_connection_request_repo(session: Session = Depends(get_session)):
    from app.adapters.persistence.connection_request_repo import SqlConnectionRequestRepository
    return SqlConnectionRequestRepository(session)


def get_current_user(
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_session),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    session_repo = SqlSessionRepository(session)
    user_id = session_repo.get_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    user_repo = SqlUserRepository(session)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
