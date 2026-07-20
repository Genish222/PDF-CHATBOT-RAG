"""Mapping utilities between domain models and LangChain types."""

from langchain_core.documents import Document

from src.domain.models.document import ChunkMetadata, DocumentChunk, RetrievedChunk


def chunk_to_langchain_document(chunk: DocumentChunk) -> Document:
    """Convert a domain chunk to a LangChain ``Document``.

    Args:
        chunk: Domain document chunk.

    Returns:
        LangChain document with equivalent content and metadata.
    """
    return Document(
        page_content=chunk.content,
        metadata={
            "source": chunk.metadata.source,
            "page": chunk.metadata.page,
            "chunk_index": chunk.metadata.chunk_index,
        },
    )


def langchain_document_to_chunk(document: Document, *, score: float) -> RetrievedChunk:
    """Convert a LangChain ``Document`` into a domain ``RetrievedChunk``.

    Args:
        document: LangChain document returned by vector search.
        score: Relevance score mapped to the domain convention (higher is better).

    Returns:
        Retrieved chunk with normalized domain metadata.
    """
    metadata = document.metadata
    source = str(metadata.get("source", "unknown"))
    page_value = metadata.get("page")
    page = int(page_value) if page_value is not None else None
    chunk_index = int(metadata.get("chunk_index", 0))

    chunk = DocumentChunk(
        content=document.page_content,
        metadata=ChunkMetadata(
            source=source,
            page=page,
            chunk_index=chunk_index,
        ),
    )
    return RetrievedChunk(chunk=chunk, score=score)


def distance_to_relevance_score(distance: float) -> float:
    """Convert a vector distance metric into a higher-is-better relevance score.

    Args:
        distance: Distance returned by FAISS/LangChain similarity search.

    Returns:
        Relevance score where larger values indicate stronger matches.
    """
    return 1.0 / (1.0 + float(distance))
