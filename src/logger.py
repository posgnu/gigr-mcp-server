"""Centralized logging configuration for the application."""

import logging
import sys
from pathlib import Path
from typing import Any

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Path | None = None,
    console: bool = True,
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.

    Args:
        name: Logger name (typically __name__ from the calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console: Whether to output to console (stdout)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name.

    Args:
        name: Logger name (typically __name__ from the calling module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter:
    """Context manager for temporarily changing log level."""

    def __init__(self, logger: logging.Logger, level: str):
        self.logger = logger
        self.new_level = getattr(logging, level.upper())
        self.original_level: int | None = None

    def __enter__(self) -> logging.Logger:
        self.original_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.original_level is not None:
            self.logger.setLevel(self.original_level)
