"""Chat-related domain models."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.models.document import RetrievedChunk


class MessageRole(StrEnum):
    """Supported roles in a chat conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """A single message in a chat conversation.

    Attributes:
        role: Speaker role for the message.
        content: Message text content.
    """

    model_config = ConfigDict(frozen=True)

    role: MessageRole
    content: str = Field(..., min_length=1, description="Message text content.")

    @field_validator("content", mode="before")
    @classmethod
    def strip_content(cls, value: object) -> str:
        """Normalize message content by trimming surrounding whitespace."""
        if value is None:
            raise ValueError("Message content is required.")

        normalized = str(value).strip()
        if not normalized:
            raise ValueError("Message content must not be empty.")

        return normalized


class SourceCitation(BaseModel):
    """A source reference supporting a generated answer.

    Attributes:
        source: Source document filename.
        page: 1-based page number, if available.
        excerpt: Relevant excerpt from the source chunk.
        score: Similarity score of the retrieved chunk.
    """

    model_config = ConfigDict(frozen=True)

    source: str = Field(..., min_length=1)
    page: int | None = Field(default=None, ge=1)
    excerpt: str = Field(..., min_length=1)
    score: float

    @classmethod
    def from_retrieved_chunk(
        cls,
        retrieved: RetrievedChunk,
        *,
        max_excerpt_length: int = 300,
    ) -> "SourceCitation":
        """Build a citation from a retrieved chunk.

        Args:
            retrieved: Chunk returned by vector similarity search.
            max_excerpt_length: Maximum number of characters in the excerpt.

        Returns:
            Source citation suitable for display in the UI.
        """
        excerpt = retrieved.chunk.content
        if len(excerpt) > max_excerpt_length:
            excerpt = f"{excerpt[: max_excerpt_length - 3].rstrip()}..."

        return cls(
            source=retrieved.chunk.metadata.source,
            page=retrieved.chunk.metadata.page,
            excerpt=excerpt,
            score=retrieved.score,
        )


class ChatResponse(BaseModel):
    """Response returned by the RAG chat use case.

    Attributes:
        answer: Generated natural-language answer.
        sources: Supporting source citations used to produce the answer.
    """

    model_config = ConfigDict(frozen=True)

    answer: str = Field(..., min_length=1)
    sources: tuple[SourceCitation, ...] = Field(default_factory=tuple)

    @field_validator("answer", mode="before")
    @classmethod
    def strip_answer(cls, value: object) -> str:
        """Normalize answer text by trimming surrounding whitespace."""
        if value is None:
            raise ValueError("Answer text is required.")

        normalized = str(value).strip()
        if not normalized:
            raise ValueError("Answer text must not be empty.")

        return normalized
