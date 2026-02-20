from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from app.core.enums import ConnectionSource, OpportunityType


@dataclass
class User:
    id: str
    name: str
    bio: str
    skills: list[str]
    interests: list[str]
    open_to: list[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Opportunity:
    id: str
    title: str
    description: str
    type: OpportunityType
    posted_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)


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
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Connection:
    id: str
    user_a: str
    user_b: str
    source: ConnectionSource
    strength: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)


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
