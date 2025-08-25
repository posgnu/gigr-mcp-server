# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server implementation with DuckDB integration. The server provides AI models with direct access to a DuckDB database through MCP tools, enabling SQL query execution, schema inspection, and data import/export capabilities.

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

## DuckDB Integration

### Database Configuration

- **Database Path**: `./data/gigr.duckdb` (file-based persistence)
- **Connection**: Singleton pattern with connection pooling
- **Auto-creation**: Database and data directory created automatically

### Available MCP Tools

#### Query Execution

- `execute_query`: Execute SELECT queries with structured JSON output
  - Parameters: `query` (str), `parameters` (optional list)
  - Returns: Structured result with columns, rows, row_count

- `execute_statement`: Execute DDL/DML statements (CREATE, INSERT, UPDATE, DELETE)
  - Parameters: `statement` (str), `parameters` (optional list)
  - Returns: Affected rows count and success status

#### Schema Inspection

- `list_tables`: Get all tables in the database
- `list_views`: Get all views in the database
- `describe_table`: Get table schema (columns, types, constraints)
- `get_table_stats`: Get table statistics (row count, size)

#### Data Import/Export

- `import_csv`: Import CSV file into a table
  - Parameters: `file_path`, `table_name`, `header`, `delimiter`

- `export_table`: Export table to CSV or Parquet format
  - Parameters: `table_name`, `file_path`, `format`

### Available MCP Resources

- `duckdb://status`: Current database status and statistics
- `duckdb://schema`: Complete database schema information

### Usage Examples

#### Creating a Table

```sql
execute_statement("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR, email VARCHAR)")
```

#### Inserting Data

```sql
execute_statement("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
```

#### Querying Data

```sql
execute_query("SELECT * FROM users WHERE name LIKE ?", ["%Alice%"])
```

#### Importing CSV

```python
import_csv("/path/to/data.csv", "my_table", header=True, delimiter=",")
```

### Safety Features

- Query timeout mechanism for long-running queries
- Proper exception handling with meaningful error messages
- Transaction support with automatic rollback on errors
- Prepared statements for SQL injection prevention

### Common Query Patterns

```sql
-- Aggregations
SELECT COUNT(*), AVG(price) FROM products GROUP BY category

-- Joins
SELECT o.*, c.name FROM orders o JOIN customers c ON o.customer_id = c.id

-- Window functions
SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) as rank FROM products

-- CTEs
WITH ranked_products AS (
  SELECT *, RANK() OVER (ORDER BY sales DESC) as rank
  FROM products
)
SELECT * FROM ranked_products WHERE rank <= 10
```

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

## Git Commit Guidelines

### Use Conventional Commits Format

Follow the Conventional Commits specification (<https://www.conventionalcommits.org/>):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring without feature changes
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks, dependency updates
- `perf`: Performance improvements
- `ci`: CI/CD changes

Examples:

- `feat: add DuckDB query execution tools`
- `fix: resolve execute_statement fetchone() error`
- `docs: update README with installation instructions`
- `chore: update dependencies to latest versions`

### DO NOT Include Attribution Lines

When making commits, DO NOT include the following lines:

- 🤖 Generated with [Claude Code](https://claude.ai/code)
- Co-Authored-By: Claude <noreply@anthropic.com>

Keep commit messages clean and professional without these attribution lines.
