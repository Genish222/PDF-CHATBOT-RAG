"""Document-related domain models."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PDFPage(BaseModel):
    """Extracted text content from a single PDF page.

    Attributes:
        page_number: 1-based page index within the source document.
        text: Raw text extracted from the page.
    """

    model_config = ConfigDict(frozen=True)

    page_number: int = Field(..., ge=1, description="1-based page number.")
    text: str = Field(..., min_length=1, description="Extracted page text.")

    @field_validator("text", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> str:
        """Normalize page text by trimming surrounding whitespace."""
        if value is None:
            raise ValueError("Page text is required.")

        normalized = str(value).strip()
        if not normalized:
            raise ValueError("Page text must not be empty.")

        return normalized


class PDFDocument(BaseModel):
    """Structured representation of a loaded PDF document.

    Attributes:
        filename: Original name of the uploaded PDF file.
        source_path: Absolute or relative path to the PDF on disk.
        pages: Ordered list of extracted pages.
    """

    model_config = ConfigDict(frozen=True)

    filename: str = Field(..., min_length=1, description="Original PDF filename.")
    source_path: Path = Field(..., description="Filesystem path to the PDF.")
    pages: tuple[PDFPage, ...] = Field(
        ...,
        min_length=1,
        description="Non-empty collection of extracted pages.",
    )

    @property
    def page_count(self) -> int:
        """Return the total number of pages in the document."""
        return len(self.pages)

    @property
    def total_characters(self) -> int:
        """Return the combined character count across all pages."""
        return sum(len(page.text) for page in self.pages)


class ChunkMetadata(BaseModel):
    """Metadata describing the origin of a text chunk.

    Attributes:
        source: Source document filename.
        page: 1-based page number, if applicable.
        chunk_index: Zero-based index of the chunk within the document.
    """

    model_config = ConfigDict(frozen=True)

    source: str = Field(..., min_length=1, description="Source document name.")
    page: int | None = Field(default=None, ge=1, description="1-based page number.")
    chunk_index: int = Field(..., ge=0, description="Zero-based chunk index.")


class DocumentChunk(BaseModel):
    """A text chunk prepared for embedding and retrieval.

    Attributes:
        content: Chunk text content.
        metadata: Provenance metadata for citations.
    """

    model_config = ConfigDict(frozen=True)

    content: str = Field(..., min_length=1, description="Chunk text content.")
    metadata: ChunkMetadata

    @field_validator("content", mode="before")
    @classmethod
    def strip_content(cls, value: object) -> str:
        """Normalize chunk content by trimming surrounding whitespace."""
        if value is None:
            raise ValueError("Chunk content is required.")

        normalized = str(value).strip()
        if not normalized:
            raise ValueError("Chunk content must not be empty.")

        return normalized


class RetrievedChunk(BaseModel):
    """A document chunk returned by similarity search.

    Attributes:
        chunk: Matching document chunk.
        score: Similarity score (higher indicates stronger relevance).
    """

    model_config = ConfigDict(frozen=True)

    chunk: DocumentChunk
    score: float = Field(..., description="Similarity score for the match.")


class IngestionResult(BaseModel):
    """Outcome of indexing a PDF document into the vector store.

    Attributes:
        document_name: Name of the ingested document.
        chunk_count: Number of chunks stored.
        page_count: Number of pages processed.
        total_characters: Combined character count of ingested content.
    """

    model_config = ConfigDict(frozen=True)

    document_name: str = Field(..., min_length=1)
    chunk_count: int = Field(..., ge=1)
    page_count: int = Field(..., ge=1)
    total_characters: int = Field(..., ge=1)
