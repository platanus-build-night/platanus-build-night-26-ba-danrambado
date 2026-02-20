from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    @abstractmethod
    def upsert_profile(self, user_id: str, text: str, metadata: dict) -> None:
        """Embed and store a user profile."""
        ...

    @abstractmethod
    def search_similar(self, query_text: str, n_results: int = 15) -> list[dict]:
        """
        Return the top-n most similar profiles to the query text.
        Each result: {"user_id": str, "score": float, "metadata": dict}
        """
        ...

    @abstractmethod
    def delete_profile(self, user_id: str) -> None: ...
