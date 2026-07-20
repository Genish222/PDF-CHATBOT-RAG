"""Document ingestion and indexing use cases."""

import shutil
from pathlib import Path
from uuid import uuid4

from src.config.logging_config import get_logger
from src.config.settings import Settings
from src.domain.exceptions import DocumentValidationError
from src.domain.interfaces import PDFLoaderPort, TextSplitterPort, VectorStorePort
from src.domain.models.document import IngestionResult

_PDF_SUFFIX = ".pdf"


class DocumentService:
    """Orchestrate PDF ingestion, chunking, indexing, and persistence."""

    def __init__(
        self,
        pdf_loader: PDFLoaderPort,
        text_splitter: TextSplitterPort,
        vector_store: VectorStorePort,
        settings: Settings,
    ) -> None:
        """Initialize the document service with required dependencies.

        Args:
            pdf_loader: Adapter for loading PDF documents.
            text_splitter: Adapter for splitting documents into chunks.
            vector_store: Adapter for storing and retrieving embeddings.
            settings: Validated application settings.
        """
        self._pdf_loader = pdf_loader
        self._text_splitter = text_splitter
        self._vector_store = vector_store
        self._settings = settings
        self._logger = get_logger(__name__)

    def initialize_index(self) -> bool:
        """Load a previously persisted vector store if one exists.

        Returns:
            ``True`` if an existing index was loaded, ``False`` otherwise.
        """
        self._logger.info("Initializing vector store from persisted index.")
        loaded = self._vector_store.load()
        self._logger.info("Vector store initialization complete | loaded=%s", loaded)
        return loaded

    def is_index_ready(self) -> bool:
        """Return whether the vector store contains indexed document chunks."""
        return not self._vector_store.is_empty()

    def save_upload(self, filename: str, content: bytes) -> Path:
        """Validate and persist an uploaded PDF to the configured upload directory.

        Args:
            filename: Original filename of the uploaded PDF.
            content: Raw PDF file bytes.

        Returns:
            Path to the saved PDF file.

        Raises:
            DocumentValidationError: If upload validation fails.
        """
        safe_name = self._build_safe_filename(filename)
        self._validate_upload(filename=safe_name, content=content)

        destination = self._settings.upload_path / safe_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

        self._logger.info(
            "Saved uploaded PDF | filename=%s | size_bytes=%d | path=%s",
            safe_name,
            len(content),
            destination,
        )
        return destination

    def ingest_pdf(self, file_path: Path) -> IngestionResult:
        """Load, chunk, index, and persist a PDF document.

        Args:
            file_path: Path to the PDF file on disk.

        Returns:
            Summary of the ingestion operation.

        Raises:
            DocumentValidationError: If the document fails validation.
            PDFLoadError: If the PDF cannot be loaded.
            VectorStoreError: If indexing or persistence fails.
        """
        resolved_path = file_path.resolve()
        self._logger.info("Starting PDF ingestion | path=%s", resolved_path)

        document = self._pdf_loader.load(resolved_path)
        chunks = self._text_splitter.split_document(document)
        chunk_count = self._vector_store.add_chunks(chunks)
        self._vector_store.persist()

        result = IngestionResult(
            document_name=document.filename,
            chunk_count=chunk_count,
            page_count=document.page_count,
            total_characters=document.total_characters,
        )

        self._logger.info(
            "Completed PDF ingestion | document=%s | chunks=%d | pages=%d",
            result.document_name,
            result.chunk_count,
            result.page_count,
        )
        return result

    def ingest_upload(self, filename: str, content: bytes) -> IngestionResult:
        """Save an uploaded PDF and ingest it into the vector store.

        Args:
            filename: Original filename of the uploaded PDF.
            content: Raw PDF file bytes.

        Returns:
            Summary of the ingestion operation.
        """
        saved_path = self.save_upload(filename, content)
        try:
            return self.ingest_pdf(saved_path)
        except Exception:
            self._logger.exception(
                "Ingestion failed after upload | path=%s",
                saved_path,
            )
            raise

    def _validate_upload(self, filename: str, content: bytes) -> None:
        """Validate uploaded PDF metadata and size."""
        if not filename.lower().endswith(_PDF_SUFFIX):
            raise DocumentValidationError(
                f"Unsupported file type for '{filename}'. Only PDF uploads are supported."
            )

        if not content:
            raise DocumentValidationError(f"Uploaded file '{filename}' is empty.")

        if len(content) > self._settings.max_file_size:
            max_size_mb = self._settings.max_file_size / (1024 * 1024)
            raise DocumentValidationError(
                f"Uploaded file '{filename}' exceeds the maximum allowed size "
                f"of {max_size_mb:.1f} MiB."
            )

    def _build_safe_filename(self, filename: str) -> str:
        """Build a sanitized, collision-resistant filename for storage."""
        original_name = Path(filename).name.strip()
        if not original_name:
            raise DocumentValidationError("Uploaded filename must not be empty.")

        if not original_name.lower().endswith(_PDF_SUFFIX):
            raise DocumentValidationError(
                f"Unsupported file type for '{original_name}'. Only PDF uploads are supported."
            )

        sanitized = "".join(
            character if character.isalnum() or character in {"-", "_", "."} else "_"
            for character in original_name
        )
        return f"{uuid4().hex[:8]}_{sanitized}"
