"""PyPDF-based PDF loader adapter."""

from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from src.config.settings import Settings
from src.domain.exceptions import DocumentValidationError, PDFLoadError
from src.domain.interfaces import PDFLoaderPort
from src.domain.models.document import PDFDocument, PDFPage
from src.infrastructure.logging import InfrastructureLogger, get_infrastructure_logger

_PDF_SUFFIX = ".pdf"


class PyPDFLoader(PDFLoaderPort):
    """Load PDF documents using the PyPDF library."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the loader with application settings.

        Args:
            settings: Validated application settings.
        """
        self._settings = settings
        self._logger = InfrastructureLogger(get_infrastructure_logger(__name__))

    def load(self, file_path: Path) -> PDFDocument:
        """Extract text content from a PDF file.

        Args:
            file_path: Path to the PDF file on disk.

        Returns:
            Structured PDF document with per-page text content.

        Raises:
            DocumentValidationError: If validation rules are violated.
            PDFLoadError: If the PDF cannot be read or parsed.
        """
        resolved_path = file_path.resolve()
        self._logger.operation_start("pdf_load", path=str(resolved_path))

        try:
            self._validate_file(resolved_path)
            pages = self._extract_pages(resolved_path)
            document = PDFDocument(
                filename=resolved_path.name,
                source_path=resolved_path,
                pages=tuple(pages),
            )
        except (DocumentValidationError, PDFLoadError):
            raise
        except Exception as exc:
            self._logger.operation_failure("pdf_load", exc, path=str(resolved_path))
            raise PDFLoadError(
                f"Unexpected error while loading PDF: {resolved_path.name}",
                cause=exc,
            ) from exc

        self._logger.operation_success(
            "pdf_load",
            path=str(resolved_path),
            pages=document.page_count,
            characters=document.total_characters,
        )
        return document

    def _validate_file(self, file_path: Path) -> None:
        """Validate PDF file existence, type, and size."""
        if not file_path.exists():
            raise DocumentValidationError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise DocumentValidationError(f"Path is not a file: {file_path}")

        if file_path.suffix.lower() != _PDF_SUFFIX:
            raise DocumentValidationError(
                f"Unsupported file type '{file_path.suffix}'. Expected a PDF file."
            )

        file_size = file_path.stat().st_size
        if file_size == 0:
            raise DocumentValidationError(f"File is empty: {file_path.name}")

        if file_size > self._settings.max_file_size:
            max_size_mb = self._settings.max_file_size / (1024 * 1024)
            raise DocumentValidationError(
                f"File '{file_path.name}' exceeds the maximum allowed size "
                f"of {max_size_mb:.1f} MiB."
            )

    def _extract_pages(self, file_path: Path) -> list[PDFPage]:
        """Extract non-empty pages from the PDF."""
        try:
            reader = PdfReader(str(file_path))
        except PdfReadError as exc:
            raise PDFLoadError(
                f"Failed to parse PDF: {file_path.name}",
                cause=exc,
            ) from exc

        if reader.is_encrypted:
            try:
                if reader.decrypt("") == 0:
                    raise PDFLoadError(
                        f"PDF is encrypted and cannot be decrypted: {file_path.name}"
                    )
            except Exception as exc:
                raise PDFLoadError(
                    f"PDF is encrypted and cannot be read: {file_path.name}",
                    cause=exc,
                ) from exc

        pages: list[PDFPage] = []
        for index, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            text = raw_text.strip()
            if not text:
                continue

            pages.append(PDFPage(page_number=index, text=text))

        if not pages:
            raise PDFLoadError(
                f"No extractable text found in PDF: {file_path.name}. "
                "The document may contain only scanned images."
            )

        return pages
