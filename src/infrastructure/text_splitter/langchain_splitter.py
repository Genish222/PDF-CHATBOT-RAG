"""LangChain-based text splitter adapter."""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config.settings import Settings
from src.domain.exceptions import DocumentValidationError
from src.domain.interfaces import TextSplitterPort
from src.domain.models.document import ChunkMetadata, DocumentChunk, PDFDocument
from src.infrastructure.logging import InfrastructureLogger, get_infrastructure_logger


class LangChainTextSplitter(TextSplitterPort):
    """Split PDF documents into retrieval-ready chunks using LangChain."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the splitter with chunk configuration from settings.

        Args:
            settings: Validated application settings.
        """
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
        self._logger = InfrastructureLogger(get_infrastructure_logger(__name__))

    def split_document(self, document: PDFDocument) -> list[DocumentChunk]:
        """Split a PDF document into embeddable text chunks.

        Args:
            document: Loaded PDF document to split.

        Returns:
            Ordered list of document chunks ready for embedding.

        Raises:
            DocumentValidationError: If no valid chunks can be produced.
        """
        self._logger.operation_start(
            "text_split",
            filename=document.filename,
            pages=document.page_count,
        )

        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for page in document.pages:
            split_texts = self._splitter.split_text(page.text)
            for text in split_texts:
                normalized = text.strip()
                if not normalized:
                    continue

                chunks.append(
                    DocumentChunk(
                        content=normalized,
                        metadata=ChunkMetadata(
                            source=document.filename,
                            page=page.page_number,
                            chunk_index=chunk_index,
                        ),
                    )
                )
                chunk_index += 1

        if not chunks:
            raise DocumentValidationError(
                f"No text chunks could be created from document: {document.filename}"
            )

        self._logger.operation_success(
            "text_split",
            filename=document.filename,
            chunk_count=len(chunks),
        )
        return chunks
