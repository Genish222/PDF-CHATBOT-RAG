"""Logging helpers for infrastructure adapters."""

import logging
from typing import Any

from src.config.logging_config import get_logger


def get_infrastructure_logger(name: str) -> logging.Logger:
    """Return a logger for an infrastructure adapter module.

    Args:
        name: Module name, typically ``__name__``.

    Returns:
        Configured logger instance.
    """
    return get_logger(name)


class InfrastructureLogger:
    """Provide consistent structured logging for adapter operations."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def operation_start(self, operation: str, **context: Any) -> None:
        """Log the start of an infrastructure operation."""
        self._logger.debug("Starting %s | context=%s", operation, context)

    def operation_success(self, operation: str, **context: Any) -> None:
        """Log the successful completion of an infrastructure operation."""
        self._logger.info("Completed %s | context=%s", operation, context)

    def operation_failure(
        self,
        operation: str,
        exc: Exception,
        **context: Any,
    ) -> None:
        """Log a failed infrastructure operation with exception details."""
        self._logger.error(
            "Failed %s | context=%s | error=%s",
            operation,
            context,
            exc,
            exc_info=True,
        )
