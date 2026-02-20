from app.core.entities import User
from app.ports.embedding_port import EmbeddingPort
from app.ports.repositories import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository, embedding: EmbeddingPort):
        self._repo = user_repo
        self._embedding = embedding

    def get_all(self) -> list[User]:
        return self._repo.get_all()

    def get_by_id(self, user_id: str) -> User | None:
        return self._repo.get_by_id(user_id)

    def create(self, user: User) -> User:
        created = self._repo.create(user)
        self._sync_embedding(created)
        return created

    def _sync_embedding(self, user: User) -> None:
        text = self._build_embedding_text(user)
        metadata = {
            "name": user.name,
            "open_to": ",".join(user.open_to),
        }
        self._embedding.upsert_profile(user.id, text, metadata)

    @staticmethod
    def _build_embedding_text(user: User) -> str:
        parts = [
            user.bio,
            f"Skills: {', '.join(user.skills)}",
            f"Interests: {', '.join(user.interests)}",
            f"Open to: {', '.join(user.open_to)}",
        ]
        return ". ".join(parts)
