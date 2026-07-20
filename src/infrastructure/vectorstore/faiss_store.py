"""FAISS vector store adapter."""

from collections.abc import Sequence
from typing import Final

from langchain_community.vectorstores import FAISS

from src.config.settings import Settings
from src.domain.exceptions import VectorStoreError
from src.domain.interfaces import VectorStorePort
from src.domain.models.document import DocumentChunk, RetrievedChunk
from src.infrastructure.embeddings.gemini_embeddings import GeminiEmbeddingsAdapter
from src.infrastructure.logging import InfrastructureLogger, get_infrastructure_logger
from src.infrastructure.mappers.document_mapper import (
    chunk_to_langchain_document,
    distance_to_relevance_score,
    langchain_document_to_chunk,
)

_INDEX_DIR_NAME: Final[str] = "faiss_index"
_INDEX_FILE_NAME: Final[str] = "index.faiss"


class FAISSVectorStore(VectorStorePort):
    """Persist and query document embeddings using a FAISS index."""

    def __init__(
        self,
        settings: Settings,
        embeddings: GeminiEmbeddingsAdapter,
    ) -> None:
        """Initialize the vector store adapter.

        Args:
            settings: Validated application settings.
            embeddings: Gemini embeddings adapter used for indexing and search.
        """
        self._settings = settings
        self._embeddings = embeddings
        self._store: FAISS | None = None
        self._index_path = settings.vector_store_path / _INDEX_DIR_NAME
        self._logger = InfrastructureLogger(get_infrastructure_logger(__name__))

    def add_chunks(self, chunks: Sequence[DocumentChunk]) -> int:
        """Add document chunks to the vector store.

        Args:
            chunks: Non-empty sequence of document chunks to index.

        Returns:
            Number of chunks successfully added.

        Raises:
            VectorStoreError: If indexing fails.
        """
        if not chunks:
            raise VectorStoreError("Cannot add an empty chunk batch.")

        documents = [chunk_to_langchain_document(chunk) for chunk in chunks]
        self._logger.operation_start("vectorstore_add", chunk_count=len(documents))

        try:
            if self._store is None:
                self._store = FAISS.from_documents(
                    documents,
                    self._embeddings.langchain_embeddings,
                )
            else:
                self._store.add_documents(documents)
        except Exception as exc:
            self._logger.operation_failure(
                "vectorstore_add",
                exc,
                chunk_count=len(documents),
            )
            raise VectorStoreError(
                "Failed to add document chunks to the FAISS index.",
                cause=exc,
            ) from exc

        self._logger.operation_success(
            "vectorstore_add",
            chunk_count=len(documents),
        )
        return len(documents)

    def similarity_search(self, query: str, top_k: int) -> list[RetrievedChunk]:
        """Retrieve the most relevant chunks for a query.

        Args:
            query: Natural-language search query.
            top_k: Maximum number of results to return.

        Returns:
            Retrieved chunks ordered by descending relevance.

        Raises:
            VectorStoreError: If search fails.
        """
        normalized_query = query.strip()
        if not normalized_query:
            raise VectorStoreError("Search query must not be empty.")

        if top_k < 1:
            return []

        if self._store is None:
            self._logger.operation_success(
                "vectorstore_search",
                query_length=len(normalized_query),
                result_count=0,
                reason="empty_store",
            )
            return []

        self._logger.operation_start(
            "vectorstore_search",
            query_length=len(normalized_query),
            top_k=top_k,
        )

        try:
            raw_results = self._store.similarity_search_with_score(
                normalized_query,
                k=top_k,
            )
        except Exception as exc:
            self._logger.operation_failure(
                "vectorstore_search",
                exc,
                query_length=len(normalized_query),
                top_k=top_k,
            )
            raise VectorStoreError(
                "Failed to execute FAISS similarity search.",
                cause=exc,
            ) from exc

        results = [
            langchain_document_to_chunk(
                document,
                score=distance_to_relevance_score(distance),
            )
            for document, distance in raw_results
        ]

        self._logger.operation_success(
            "vectorstore_search",
            query_length=len(normalized_query),
            result_count=len(results),
        )
        return results

    def persist(self) -> None:
        """Persist the in-memory vector store to disk.

        Raises:
            VectorStoreError: If persistence fails.
        """
        if self._store is None:
            raise VectorStoreError("Cannot persist an empty vector store.")

        self._index_path.mkdir(parents=True, exist_ok=True)
        self._logger.operation_start("vectorstore_persist", path=str(self._index_path))

        try:
            self._store.save_local(str(self._index_path))
        except Exception as exc:
            self._logger.operation_failure(
                "vectorstore_persist",
                exc,
                path=str(self._index_path),
            )
            raise VectorStoreError(
                "Failed to persist FAISS index to disk.",
                cause=exc,
            ) from exc

        self._logger.operation_success(
            "vectorstore_persist",
            path=str(self._index_path),
        )

    def load(self) -> bool:
        """Load a previously persisted vector store from disk.

        Returns:
            ``True`` if a persisted store was loaded, ``False`` if none exists.

        Raises:
            VectorStoreError: If loading fails due to corruption or I/O errors.
        """
        index_file = self._index_path / _INDEX_FILE_NAME
        if not index_file.exists():
            self._logger.operation_success(
                "vectorstore_load",
                path=str(self._index_path),
                loaded=False,
                reason="missing_index",
            )
            return False

        self._logger.operation_start("vectorstore_load", path=str(self._index_path))

        try:
            self._store = FAISS.load_local(
                folder_path=str(self._index_path),
                embeddings=self._embeddings.langchain_embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception as exc:
            self._logger.operation_failure(
                "vectorstore_load",
                exc,
                path=str(self._index_path),
            )
            raise VectorStoreError(
                "Failed to load persisted FAISS index.",
                cause=exc,
            ) from exc

        self._logger.operation_success(
            "vectorstore_load",
            path=str(self._index_path),
            loaded=True,
        )
        return True

    def is_empty(self) -> bool:
        """Return whether the vector store contains indexed chunks."""
        return self._store is None
