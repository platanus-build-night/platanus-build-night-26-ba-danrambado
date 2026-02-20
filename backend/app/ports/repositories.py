from abc import ABC, abstractmethod
from typing import Optional

from app.core.entities import Connection, ConnectionRequest, Feedback, Match, Opportunity, User


class UserRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[User]: ...

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def create(self, user: User) -> User: ...


class OpportunityRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Opportunity]: ...

    @abstractmethod
    def get_by_id(self, opportunity_id: str) -> Optional[Opportunity]: ...

    @abstractmethod
    def create(self, opportunity: Opportunity) -> Opportunity: ...


class MatchRepository(ABC):
    @abstractmethod
    def get_by_opportunity(self, opportunity_id: str) -> list[Match]: ...

    @abstractmethod
    def create_batch(self, matches: list[Match]) -> list[Match]: ...


class ConnectionRepository(ABC):
    @abstractmethod
    def get_connections(self, user_id: str) -> list[Connection]: ...

    @abstractmethod
    def get_second_degree(self, user_id: str) -> dict[str, list[str]]:
        """Returns {user_id: [shared_connection_names]} for 2nd-degree connections."""
        ...

    @abstractmethod
    def create(self, connection: Connection) -> Connection: ...

    @abstractmethod
    def create_batch(self, connections: list[Connection]) -> list[Connection]: ...


class SessionRepository(ABC):
    @abstractmethod
    def create(self, session_id: str, user_id: str) -> None: ...

    @abstractmethod
    def get_user_id(self, session_id: str) -> Optional[str]: ...

    @abstractmethod
    def delete(self, session_id: str) -> None: ...


class FeedbackRepository(ABC):
    @abstractmethod
    def get_by_user(self, to_user_id: str) -> list[Feedback]: ...

    @abstractmethod
    def create(self, feedback: Feedback) -> Feedback: ...

    @abstractmethod
    def has_feedback(self, from_user_id: str, to_user_id: str, opportunity_type: str) -> bool: ...


class ConnectionRequestRepository(ABC):
    @abstractmethod
    def create(self, req: ConnectionRequest) -> ConnectionRequest: ...

    @abstractmethod
    def get_by_id(self, request_id: str) -> Optional[ConnectionRequest]: ...

    @abstractmethod
    def get_incoming(self, user_id: str) -> list[ConnectionRequest]: ...

    @abstractmethod
    def get_outgoing(self, user_id: str) -> list[ConnectionRequest]: ...

    @abstractmethod
    def update_status(self, request_id: str, status: str) -> Optional[ConnectionRequest]: ...

    @abstractmethod
    def exists(self, from_user_id: str, to_user_id: str, opportunity_id: str) -> bool: ...
