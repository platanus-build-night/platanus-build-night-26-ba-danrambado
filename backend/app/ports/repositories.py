from abc import ABC, abstractmethod
from typing import Optional

from app.core.entities import Connection, Match, Opportunity, User


class UserRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[User]: ...

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]: ...

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
