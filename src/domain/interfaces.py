"""Abstract ports defining infrastructure contracts."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

from src.domain.models.document import DocumentChunk, PDFDocument, RetrievedChunk


class PDFLoaderPort(ABC):
    """Port for loading PDF documents from disk."""

    @abstractmethod
    def load(self, file_path: Path) -> PDFDocument:
        """Extract text content from a PDF file.

        Args:
            file_path: Path to the PDF file on disk.

        Returns:
            Structured PDF document with per-page text content.

        Raises:
            PDFLoadError: If the file cannot be read or parsed.
            DocumentValidationError: If the file is not a valid PDF.
        """


class TextSplitterPort(ABC):
    """Port for splitting document text into retrieval chunks."""

    @abstractmethod
    def split_document(self, document: PDFDocument) -> list[DocumentChunk]:
        """Split a PDF document into embeddable text chunks.

        Args:
            document: Loaded PDF document to split.

        Returns:
            Ordered list of document chunks ready for embedding.
        """


class EmbeddingPort(ABC):
    """Port for generating vector embeddings from text."""

    @abstractmethod
    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate embeddings for a batch of text strings.

        Args:
            texts: Non-empty sequence of strings to embed.

        Returns:
            Embedding vectors aligned with the input texts.

        Raises:
            EmbeddingError: If embedding generation fails.
        """


class VectorStorePort(ABC):
    """Port for storing and querying document embeddings."""

    @abstractmethod
    def add_chunks(self, chunks: Sequence[DocumentChunk]) -> int:
        """Add document chunks to the vector store.

        Args:
            chunks: Non-empty sequence of document chunks to index.

        Returns:
            Number of chunks successfully added.

        Raises:
            VectorStoreError: If indexing fails.
        """

    @abstractmethod
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

    @abstractmethod
    def persist(self) -> None:
        """Persist the in-memory vector store to disk.

        Raises:
            VectorStoreError: If persistence fails.
        """

    @abstractmethod
    def load(self) -> bool:
        """Load a previously persisted vector store from disk.

        Returns:
            ``True`` if a persisted store was loaded, ``False`` if none exists.

        Raises:
            VectorStoreError: If loading fails due to corruption or I/O errors.
        """

    @abstractmethod
    def is_empty(self) -> bool:
        """Return whether the vector store contains indexed chunks."""


class LLMPort(ABC):
    """Port for generating natural-language responses."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a completion for the given prompt.

        Args:
            prompt: Fully constructed prompt including retrieved context.

        Returns:
            Generated response text.

        Raises:
            LLMError: If generation fails.
        """
