"""Domain-layer exception hierarchy."""


class DomainError(Exception):
    """Base exception for all domain-layer errors.

    Attributes:
        message: Human-readable error description.
        cause: Optional underlying exception that triggered this error.
    """

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.cause = cause


class DocumentError(DomainError):
    """Raised when document ingestion or validation fails."""


class PDFLoadError(DocumentError):
    """Raised when a PDF file cannot be read or parsed."""


class DocumentValidationError(DocumentError):
    """Raised when an uploaded document fails validation rules."""


class VectorStoreError(DomainError):
    """Raised when vector store operations fail."""


class EmbeddingError(DomainError):
    """Raised when text embedding generation fails."""


class LLMError(DomainError):
    """Raised when the language model fails to generate a response."""


class ChatError(DomainError):
    """Raised when a chat interaction cannot be completed."""
