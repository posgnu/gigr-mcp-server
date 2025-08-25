"""Pytest configuration and fixtures."""

import sys
from collections.abc import Generator
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_data() -> dict:
    """Provide sample data for tests."""
    return {
        "id": 1,
        "name": "Test Item",
        "value": 42.0,
        "active": True,
        "tags": ["test", "sample"],
    }


@pytest.fixture
def temp_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content\n")
    yield file_path
    # Cleanup happens automatically with tmp_path


@pytest.fixture
def mock_env_vars(monkeypatch) -> None:
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("TEST_VAR", "test_value")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("API_KEY", "test_api_key")


# Add more fixtures as needed for your project
