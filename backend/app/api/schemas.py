from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    bio: str
    skills: list[str]
    interests: list[str]
    open_to: list[str]


class UserResponse(BaseModel):
    id: str
    name: str
    bio: str
    skills: list[str]
    interests: list[str]
    open_to: list[str]
    created_at: datetime
    connection_count: int = 0


class OpportunityCreate(BaseModel):
    title: str
    description: str
    type: str
    posted_by: str


class OpportunityResponse(BaseModel):
    id: str
    title: str
    description: str
    type: str
    posted_by: str
    poster_name: str = ""
    created_at: datetime


class MatchResponse(BaseModel):
    id: str
    opportunity_id: str
    user_id: str
    user_name: str = ""
    user_bio: str = ""
    user_skills: list[str] = []
    score: float
    embedding_score: float
    network_score: float
    explanation: str
    rank: int
    created_at: datetime


class OpportunityDetailResponse(BaseModel):
    opportunity: OpportunityResponse
    matches: list[MatchResponse]


class ConnectionResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    source: str
    strength: float


class NetworkResponse(BaseModel):
    user: UserResponse
    connections: list[ConnectionResponse]
