"""Domain layer — models, ports, and exceptions."""

from src.domain.exceptions import (
    ChatError,
    DocumentError,
    DocumentValidationError,
    DomainError,
    EmbeddingError,
    LLMError,
    PDFLoadError,
    VectorStoreError,
)
from src.domain.interfaces import (
    EmbeddingPort,
    LLMPort,
    PDFLoaderPort,
    TextSplitterPort,
    VectorStorePort,
)
from src.domain.models import (
    ChatMessage,
    ChatResponse,
    ChunkMetadata,
    DocumentChunk,
    IngestionResult,
    MessageRole,
    PDFDocument,
    PDFPage,
    RetrievedChunk,
    SourceCitation,
)

__all__ = [
    "ChatError",
    "ChatMessage",
    "ChatResponse",
    "ChunkMetadata",
    "DocumentChunk",
    "DocumentError",
    "DocumentValidationError",
    "DomainError",
    "EmbeddingError",
    "EmbeddingPort",
    "IngestionResult",
    "LLMError",
    "LLMPort",
    "MessageRole",
    "PDFDocument",
    "PDFLoadError",
    "PDFLoaderPort",
    "PDFPage",
    "RetrievedChunk",
    "SourceCitation",
    "TextSplitterPort",
    "VectorStoreError",
    "VectorStorePort",
]
