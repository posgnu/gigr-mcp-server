"""Unit tests for main module."""

from src.main import main


def test_main_function():
    """Test that main function runs without error."""
    # This would normally capture stdout, but for simplicity
    # just ensure it doesn't crash
    try:
        main()
    except Exception as e:
        raise AssertionError("main() should not raise an exception") from e
