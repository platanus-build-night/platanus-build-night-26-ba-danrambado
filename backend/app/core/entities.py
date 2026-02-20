from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from app.core.enums import ConnectionSource, OpportunityType


@dataclass
class User:
    id: str
    name: str
    bio: str
    skills: list[str]
    interests: list[str]
    open_to: list[str]
    email: str = ""
    password_hash: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Opportunity:
    id: str
    title: str
    description: str
    type: OpportunityType
    posted_by: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Match:
    id: str
    opportunity_id: str
    user_id: str
    score: float
    embedding_score: float
    network_score: float
    explanation: str
    rank: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Connection:
    id: str
    user_a: str
    user_b: str
    source: ConnectionSource
    strength: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CandidateScore:
    """Intermediate result from Phase 1 retrieval."""

    user: User
    embedding_score: float
    network_score: float
    combined_score: float
    shared_connections: list[str] = field(default_factory=list)


@dataclass
class RankedMatch:
    """Result from Phase 2 LLM ranking."""

    user_id: str
    rank: int
    score: float
    explanation: str


@dataclass
class Feedback:
    id: str
    from_user_id: str
    to_user_id: str
    opportunity_type: str
    text: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConnectionRequest:
    id: str
    from_user_id: str
    to_user_id: str
    opportunity_id: str
    match_id: str
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
