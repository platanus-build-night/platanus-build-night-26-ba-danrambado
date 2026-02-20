from datetime import datetime

from pydantic import BaseModel


# --- Auth ---

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    bio: str = ""
    skills: list[str] = []
    interests: list[str] = []
    open_to: list[str] = []


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: "UserResponse"


# --- Users ---

class UserCreate(BaseModel):
    name: str
    bio: str
    skills: list[str]
    interests: list[str]
    open_to: list[str]


class UserResponse(BaseModel):
    id: str
    name: str
    email: str = ""
    bio: str
    skills: list[str]
    interests: list[str]
    open_to: list[str]
    created_at: datetime
    connection_count: int = 0


# --- Opportunities ---

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


# --- Network ---

class ConnectionResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    source: str
    strength: float


class NetworkMemberResponse(BaseModel):
    user: UserResponse
    degree: int
    shared_connections: list[str] = []
    connection_source: str = ""


class NetworkResponse(BaseModel):
    user: UserResponse
    connections: list[ConnectionResponse]


class LayeredNetworkResponse(BaseModel):
    first_degree: list[NetworkMemberResponse]
    second_degree: list[NetworkMemberResponse]
    pending_incoming: int = 0


class SearchResultResponse(BaseModel):
    user: UserResponse
    degree: str = "other"
    shared_connections: list[str] = []


# --- Connection Requests ---

class ConnectionRequestCreate(BaseModel):
    to_user_id: str
    opportunity_id: str
    match_id: str


class ConnectionRequestResponse(BaseModel):
    id: str
    from_user_id: str
    to_user_id: str
    opportunity_id: str
    match_id: str
    status: str
    from_user_name: str = ""
    to_user_name: str = ""
    opportunity_title: str = ""
    created_at: datetime


# --- Feedback ---

class FeedbackCreate(BaseModel):
    to_user_id: str
    opportunity_type: str
    text: str


class FeedbackResponse(BaseModel):
    id: str
    to_user_id: str
    opportunity_type: str
    created_at: datetime


class ImpressionResponse(BaseModel):
    summary: str
    by_context: dict[str, str] = {}
    feedback_count: int = 0
