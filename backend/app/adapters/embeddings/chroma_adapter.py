import chromadb

from app.config import settings
from app.ports.embedding_port import EmbeddingPort


class ChromaEmbeddingAdapter(EmbeddingPort):
    def __init__(self):
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._collection = self._client.get_or_create_collection(
            name="profiles",
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_profile(self, user_id: str, text: str, metadata: dict) -> None:
        self._collection.upsert(
            ids=[user_id],
            documents=[text],
            metadatas=[metadata],
        )

    def search_similar(self, query_text: str, n_results: int = 15) -> list[dict]:
        results = self._collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )

        items = []
        if not results["ids"] or not results["ids"][0]:
            return items

        for i, uid in enumerate(results["ids"][0]):
            distance = results["distances"][0][i] if results["distances"] else 0.0
            score = 1.0 - distance
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            items.append({"user_id": uid, "score": score, "metadata": meta})

        return items

    def delete_profile(self, user_id: str) -> None:
        try:
            self._collection.delete(ids=[user_id])
        except Exception:
            pass
