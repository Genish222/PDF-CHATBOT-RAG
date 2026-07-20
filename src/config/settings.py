"""Application settings loaded from environment variables."""

from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Final, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_CHUNK_SIZE: Final[int] = 1000
_DEFAULT_CHUNK_OVERLAP: Final[int] = 200
_DEFAULT_MAX_FILE_SIZE_BYTES: Final[int] = 10 * 1024 * 1024  # 10 MiB
_MIN_CHUNK_SIZE: Final[int] = 100
_MAX_CHUNK_SIZE: Final[int] = 10_000
_MAX_CHUNK_OVERLAP: Final[int] = 5_000
_MIN_FILE_SIZE_BYTES: Final[int] = 1024  # 1 KiB
_MAX_FILE_SIZE_BYTES: Final[int] = 100 * 1024 * 1024  # 100 MiB

_PLACEHOLDER_API_KEYS: Final[frozenset[str]] = frozenset(
    {
        "",
        "your_google_api_key_here",
        "your-api-key-here",
        "changeme",
    }
)


class LogLevel(StrEnum):
    """Supported application log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and a `.env` file.

    Environment variables are read case-insensitively. Process environment values
    take precedence over values defined in `.env`.

    Attributes:
        google_api_key: Google Gemini API key for embeddings and generation.
        model_name: Gemini model identifier used for chat completion.
        embedding_model: Gemini model identifier used for text embeddings.
        chunk_size: Maximum number of characters per document chunk.
        chunk_overlap: Number of overlapping characters between adjacent chunks.
        vector_store_path: Directory where the FAISS index is persisted.
        upload_path: Directory where uploaded PDF files are stored.
        max_file_size: Maximum allowed PDF upload size in bytes.
        log_level: Application logging verbosity.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    google_api_key: str = Field(
        ...,
        min_length=1,
        description="Google Gemini API key.",
    )
    model_name: str = Field(
        default="gemini-2.0-flash",
        min_length=1,
        max_length=128,
        description="Gemini model name used for chat completion.",
    )
    embedding_model: str = Field(
        default="models/embedding-001",
        min_length=1,
        max_length=128,
        description="Gemini model name used for text embeddings.",
    )
    chunk_size: int = Field(
        default=_DEFAULT_CHUNK_SIZE,
        ge=_MIN_CHUNK_SIZE,
        le=_MAX_CHUNK_SIZE,
        description="Maximum characters per text chunk during document ingestion.",
    )
    chunk_overlap: int = Field(
        default=_DEFAULT_CHUNK_OVERLAP,
        ge=0,
        le=_MAX_CHUNK_OVERLAP,
        description="Character overlap between consecutive text chunks.",
    )
    vector_store_path: Path = Field(
        default=Path("data/vectorstores"),
        description="Filesystem path for persisted FAISS vector store data.",
    )
    upload_path: Path = Field(
        default=Path("data/uploads"),
        description="Filesystem path for uploaded PDF documents.",
    )
    max_file_size: int = Field(
        default=_DEFAULT_MAX_FILE_SIZE_BYTES,
        ge=_MIN_FILE_SIZE_BYTES,
        le=_MAX_FILE_SIZE_BYTES,
        description="Maximum allowed PDF upload size in bytes.",
    )
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Application logging verbosity.",
    )

    @field_validator("google_api_key", mode="before")
    @classmethod
    def validate_google_api_key(cls, value: object) -> str:
        """Normalize and reject placeholder Google API keys."""
        if value is None:
            raise ValueError("GOOGLE_API_KEY is required.")

        normalized = str(value).strip()
        if normalized.lower() in _PLACEHOLDER_API_KEYS:
            raise ValueError(
                "GOOGLE_API_KEY must be set to a valid API key, not a placeholder."
            )

        return normalized

    @field_validator("model_name", "embedding_model", mode="before")
    @classmethod
    def validate_non_empty_string(cls, value: object, info) -> str:
        """Ensure model identifiers are non-empty after trimming."""
        if value is None:
            raise ValueError(f"{info.field_name.upper()} is required.")

        normalized = str(value).strip()
        if not normalized:
            raise ValueError(f"{info.field_name.upper()} must not be empty.")

        return normalized

    @field_validator("vector_store_path", "upload_path", mode="before")
    @classmethod
    def validate_path(cls, value: object, info) -> Path:
        """Convert configured paths to ``Path`` instances."""
        if value is None:
            raise ValueError(f"{info.field_name.upper()} is required.")

        path = Path(str(value).strip())
        if not str(path):
            raise ValueError(f"{info.field_name.upper()} must not be empty.")

        return path

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, value: object) -> LogLevel:
        """Normalize log level values to a supported enum member."""
        if value is None:
            return LogLevel.INFO

        normalized = str(value).strip().upper()
        try:
            return LogLevel(normalized)
        except ValueError as exc:
            supported = ", ".join(level.value for level in LogLevel)
            raise ValueError(
                f"LOG_LEVEL must be one of: {supported}. Got '{value}'."
            ) from exc

    @model_validator(mode="after")
    def validate_chunk_settings(self) -> Self:
        """Ensure chunk overlap is strictly smaller than chunk size."""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "CHUNK_OVERLAP must be less than CHUNK_SIZE "
                f"(got overlap={self.chunk_overlap}, size={self.chunk_size})."
            )

        return self

    def ensure_runtime_directories(self) -> None:
        """Create configured filesystem directories if they do not exist."""
        self.upload_path.mkdir(parents=True, exist_ok=True)
        self.vector_store_path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Return a cached, validated ``Settings`` instance.

    Returns:
        Immutable application settings loaded from the environment.

    Raises:
        pydantic.ValidationError: If required environment variables are missing or invalid.
    """
    return Settings()
