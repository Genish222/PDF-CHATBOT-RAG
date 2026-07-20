"""Google Gemini embeddings adapter."""

from collections.abc import Sequence

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config.settings import Settings
from src.domain.exceptions import EmbeddingError
from src.domain.interfaces import EmbeddingPort
from src.infrastructure.logging import InfrastructureLogger, get_infrastructure_logger


class GeminiEmbeddingsAdapter(EmbeddingPort):
    """Generate text embeddings using Google Gemini via LangChain."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Gemini embeddings client.

        Args:
            settings: Validated application settings.
        """
        self._settings = settings
        self._logger = InfrastructureLogger(get_infrastructure_logger(__name__))
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            google_api_key=settings.google_api_key,
        )

    @property
    def langchain_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """Return the underlying LangChain embeddings client.

        Returns:
            LangChain-compatible embeddings instance for vector store integration.
        """
        return self._embeddings

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate embeddings for a batch of text strings.

        Args:
            texts: Non-empty sequence of strings to embed.

        Returns:
            Embedding vectors aligned with the input texts.

        Raises:
            EmbeddingError: If embedding generation fails.
        """
        if not texts:
            raise EmbeddingError("Cannot embed an empty text batch.")

        self._logger.operation_start("embed_texts", batch_size=len(texts))

        try:
            vectors = self._embeddings.embed_documents(list(texts))
        except Exception as exc:
            self._logger.operation_failure(
                "embed_texts",
                exc,
                batch_size=len(texts),
            )
            raise EmbeddingError(
                "Failed to generate embeddings using Gemini.",
                cause=exc,
            ) from exc

        self._logger.operation_success(
            "embed_texts",
            batch_size=len(texts),
            vector_count=len(vectors),
        )
        return vectors
