"""Unit tests for logger module."""

import logging
import tempfile
from pathlib import Path

from src.logger import LoggerAdapter, get_logger, setup_logger


def test_setup_logger_basic():
    """Test basic logger setup."""
    logger = setup_logger("test_logger", level="INFO")

    assert logger.name == "test_logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0


def test_setup_logger_debug_level():
    """Test logger with DEBUG level."""
    logger = setup_logger("test_debug", level="DEBUG")

    assert logger.level == logging.DEBUG


def test_setup_logger_with_file():
    """Test logger with file output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        logger = setup_logger("test_file", level="INFO", log_file=log_file)

        # Log a message
        logger.info("Test message")

        # Check file was created and contains the message
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content
        assert "INFO" in content


def test_setup_logger_no_console():
    """Test logger without console output."""
    logger = setup_logger("test_no_console", console=False)

    # Should have no handlers since console=False and no file specified
    assert len(logger.handlers) == 0


def test_get_logger():
    """Test getting an existing logger."""
    # First create a logger
    setup_logger("test_existing", level="WARNING")

    # Get the same logger
    logger = get_logger("test_existing")

    assert logger.name == "test_existing"
    assert logger.level == logging.WARNING


def test_logger_adapter():
    """Test LoggerAdapter context manager."""
    logger = setup_logger("test_adapter", level="INFO")

    # Initial level is INFO
    assert logger.level == logging.INFO

    # Use adapter to temporarily change to DEBUG
    with LoggerAdapter(logger, "DEBUG") as log:
        assert log.level == logging.DEBUG

    # Level should be restored
    assert logger.level == logging.INFO


def test_logger_adapter_with_none():
    """Test LoggerAdapter handles None original level."""
    logger = setup_logger("test_adapter_none", level="INFO")

    adapter = LoggerAdapter(logger, "DEBUG")
    adapter.original_level = None

    # Should not raise an error
    adapter.__exit__(None, None, None)


def test_setup_logger_prevents_duplicates():
    """Test that setup_logger doesn't add duplicate handlers."""
    logger = setup_logger("test_duplicate", level="INFO")
    initial_handler_count = len(logger.handlers)

    # Call setup again
    logger = setup_logger("test_duplicate", level="DEBUG")

    # Should still have same number of handlers
    assert len(logger.handlers) == initial_handler_count
