# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server implementation using Python and the official MCP SDK. The project provides a standardized way for AI models to access tools and resources through the MCP specification.

## MCP (Model Context Protocol) Documentation

### Official Resources

- **Python SDK**: <https://github.com/modelcontextprotocol/python-sdk>
- **MCP Specification**: <https://modelcontextprotocol.io/>
- **Official MCP Servers Repository**: <https://github.com/modelcontextprotocol/servers>
- **MCP Client Quickstart**: <https://modelcontextprotocol.io/quickstart/client>

### Key Concepts

- **Tools**: Functions that can be called by AI models (decorated with `@mcp.tool()`)
- **Resources**: Data sources accessible via URI patterns (decorated with `@mcp.resource()`)
- **FastMCP**: The main server class for implementing MCP servers
- **Transports**: Communication methods (stdio, SSE, HTTP) - this server uses stdio

### Common Patterns

- Use type hints for all tool parameters and return values
- Provide comprehensive docstrings for tools and resources
- Handle both sync and async functions
- Use structured data (dicts/Pydantic models) for complex responses
- Follow URI patterns for resources (e.g., "gigr://resource/{param}")

### Development Workflow for MCP

1. Define tools using `@mcp.tool()` decorator
2. Define resources using `@mcp.resource("uri://pattern")` decorator
3. Use `await mcp.run()` to start the server
4. Test with MCP clients or AI models that support MCP

## Essential Commands

### Development Setup

```bash
# Install all dependencies (including dev)
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Activate virtual environment
poetry shell
```

### Running the MCP Server

```bash
# Run the MCP server
poetry run python -m src.main

# Or using the CLI command
poetry run gigr-mcp-server

# Or using Make
make run
```

### Testing

```bash
# Run all tests with coverage
poetry run pytest

# Run specific test file
poetry run pytest tests/unit/test_main.py

# Run specific test
poetry run pytest tests/unit/test_main.py::TestMainCLI::test_hello_default

# Run only unit tests
poetry run pytest -m unit

# Run tests without slow tests
poetry run pytest -m "not slow"

# Run with verbose output
poetry run pytest -v
```

### Code Quality

```bash
# Format code (applies changes)
poetry run black src tests
poetry run isort src tests

# Or using Make
make format

# Check formatting without changes
poetry run black --check src tests
poetry run isort --check-only src tests

# Run all linters
make lint

# Type checking
poetry run mypy src

# Security scanning
poetry run bandit -r src -ll
```

### Using Tox for Multi-Environment Testing

```bash
# Test across all Python versions
poetry run tox

# Run specific environment
poetry run tox -e py311
poetry run tox -e lint
poetry run tox -e type
```

## Project Architecture

### Directory Structure

- `src/`: Main package directory containing application code
  - Simple entry point in `main.py` with a basic Hello World implementation
- `tests/`: Test suite organized into unit and integration tests
  - Uses pytest with fixtures defined in `conftest.py`
  - Test coverage requirement: 80% minimum
- `.github/`: GitHub Actions workflows for CI/CD
  - `ci.yml`: Runs on push/PR - linting, testing across multiple Python versions
  - `release.yml`: Handles releases and Docker image publishing
  - `dependabot.yml`: Automated dependency updates

### Key Configuration Files

- `pyproject.toml`: Central configuration for Poetry, tools (black, isort, mypy, pytest, ruff)
- `pytest.ini`: Pytest configuration with coverage settings and test markers
- `tox.ini`: Multi-environment testing configuration
- `.pre-commit-config.yaml`: Git hooks for code quality (black, isort, flake8, mypy, ruff, bandit)
- `Makefile`: Convenient commands for common tasks

### Tool Configuration

The project uses inline configuration in `pyproject.toml` for:

- **Black**: Line length 88, Python 3.11+ target
- **isort**: Black-compatible profile
- **MyPy**: Strict type checking enabled
- **Ruff**: Fast linting with selected rules (E, W, F, I, B, C4, UP)
- **Coverage**: 80% minimum, excludes test files

### Docker Support

- Multi-stage Dockerfile for optimized image size
- Non-root user execution for security
- Poetry used for dependency management in container

## Development Workflow

1. Dependencies are managed through Poetry - always use `poetry add` for new packages
2. Pre-commit hooks run automatically on git commit (can be bypassed with `--no-verify` if needed)
3. Tests should maintain 80% coverage minimum
4. All code should pass black, isort, flake8, mypy, and ruff checks before committing
