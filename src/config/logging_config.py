"""Centralized logging configuration."""

import logging
import sys
from typing import Final

from src.config.settings import LogLevel, Settings

_DEFAULT_LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
_DEFAULT_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


def setup_logging(settings: Settings) -> None:
    """Configure root logging for the application.

    Args:
        settings: Validated application settings containing the desired log level.
    """
    log_level = _resolve_log_level(settings.log_level)

    logging.basicConfig(
        level=log_level,
        format=_DEFAULT_LOG_FORMAT,
        datefmt=_DEFAULT_DATE_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger with the given name.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)


def _resolve_log_level(level: LogLevel) -> int:
    """Map application log level enum values to ``logging`` constants."""
    mapping = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARNING: logging.WARNING,
        LogLevel.ERROR: logging.ERROR,
        LogLevel.CRITICAL: logging.CRITICAL,
    }
    return mapping[level]
