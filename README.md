# GIGR MCP Server

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)](http://mypy-lang.org/)
[![Linting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A Model Context Protocol (MCP) server with DuckDB integration, providing AI models with direct access to a DuckDB database through MCP tools for SQL query execution, schema inspection, and data import/export capabilities.

## Features

- **DuckDB Integration**: File-based DuckDB database with persistent storage
- **SQL Execution**: Execute SELECT queries and DDL/DML statements through MCP tools
- **Schema Inspection**: List tables, views, and describe table schemas
- **Data Import/Export**: Import CSV files and export tables to CSV/Parquet formats
- **Structured Output**: JSON-structured responses with backwards compatibility
- **MCP Resources**: Access database status and schema through MCP resources

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Development](#development)
- [Testing](#testing)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)

### Using Poetry (Recommended)

1. Install Poetry if you haven't already:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/posgnu/gigr-mcp-server.git
   cd gigr-db-mcp
   ```

3. Install dependencies:

   ```bash
   poetry install
   ```

4. Activate the virtual environment:

   ```bash
   poetry shell
   ```

### Using pip

1. Clone the repository:

   ```bash
   git clone https://github.com/posgnu/gigr-mcp-server.git
   cd gigr-db-mcp
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package:

   ```bash
   pip install -e .
   ```

## Quick Start

1. Install dependencies:

   ```bash
   poetry install
   ```

2. Run the MCP server:

   ```bash
   poetry run python -m src.main
   ```

3. Test with MCP Inspector:

   ```bash
   npx @modelcontextprotocol/inspector poetry run python -m src.main
   ```

4. Example: Create a table and query data:
   - Use `execute_statement` to create a table
   - Use `execute_query` to retrieve data
   - Use `list_tables` to see all tables
   - Use `describe_table` to inspect schema

## Usage

### Running the MCP Server

```bash
# Using poetry
poetry run python -m src.main

# Or using the CLI command
poetry run gigr-mcp-server
```

### Debugging with MCP Inspector

Use the MCP Inspector to debug and test the server:

```bash
npx @modelcontextprotocol/inspector poetry run python -m src.main
```

This will open a web interface where you can:

- View all available tools and resources
- Test tool execution with different parameters
- Inspect request/response payloads
- Debug server communication

### Configuration with Claude Desktop

1. Edit the Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the server configuration:

```json
{
  "mcpServers": {
    "gigr-mcp-server": {
      "command": "poetry",
      "args": ["run", "python", "-m", "src.main"],
      "cwd": "/path/to/gigr-db-mcp"
    }
  }
}
```

3. Restart Claude Desktop to connect to the server

## Available MCP Tools

### Query Execution

- **`execute_query`**: Execute SELECT queries with structured JSON output
  - Parameters: `query` (str), `parameters` (optional list)
  - Returns: Columns, rows, row count, and query text

- **`execute_statement`**: Execute DDL/DML statements (CREATE, INSERT, UPDATE, DELETE)
  - Parameters: `statement` (str), `parameters` (optional list)
  - Returns: Affected rows count and success status

### Schema Inspection

- **`list_tables`**: Get all tables in the database
- **`list_views`**: Get all views in the database
- **`describe_table`**: Get table schema with column details
  - Parameters: `table_name` (str)
- **`get_table_stats`**: Get table statistics (row count, size)
  - Parameters: `table_name` (str)

### Data Import/Export

- **`import_csv`**: Import CSV file into a table
  - Parameters: `file_path`, `table_name`, `header` (bool), `delimiter` (str)

- **`export_table`**: Export table to CSV or Parquet format
  - Parameters: `table_name`, `file_path`, `format` (CSV/PARQUET)

## Available MCP Resources

- **`duckdb://status`**: Current database status and statistics
- **`duckdb://schema`**: Complete database schema information

## Development

### Setting Up Development Environment

1. Install development dependencies:

   ```bash
   poetry install --with dev
   ```

2. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

3. Run pre-commit on all files (optional):

   ```bash
   pre-commit run --all-files
   ```

### Code Quality Tools

This project uses several tools to maintain code quality:

- **Black**: Code formatting

  ```bash
  poetry run black src tests
  ```

- **isort**: Import sorting

  ```bash
  poetry run isort src tests
  ```

- **Flake8**: Linting

  ```bash
  poetry run flake8 src tests
  ```

- **MyPy**: Type checking

  ```bash
  poetry run mypy src
  ```

- **Ruff**: Fast Python linter

  ```bash
  poetry run ruff check src tests
  ```

### Project Structure

```
gigr-db-mcp/
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py            # MCP server entry point with DuckDB tools
│   └── duckdb_manager.py  # DuckDB connection manager
├── data/                   # Database storage (auto-created)
│   └── gigr.duckdb        # File-based DuckDB database
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Pytest configuration
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                   # Documentation
├── .github/               # GitHub specific files
│   ├── workflows/         # GitHub Actions
│   └── ISSUE_TEMPLATE/    # Issue templates
├── pyproject.toml         # Project configuration
├── poetry.lock           # Locked dependencies
├── CLAUDE.md             # Claude-specific instructions
├── README.md             # This file
├── .gitignore           # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks
├── Dockerfile           # Docker configuration
├── pytest.ini          # Pytest configuration
└── tox.ini            # Tox configuration
```

## Testing

### Running Tests

Run all tests:

```bash
poetry run pytest
```

Run with coverage:

```bash
poetry run pytest --cov=src --cov-report=html
```

Run specific test markers:

```bash
# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration

# Skip slow tests
poetry run pytest -m "not slow"
```

### Using Tox

Run tests across multiple Python versions:

```bash
poetry run tox
```

Run specific environments:

```bash
# Run tests
poetry run tox -e py311

# Run linting
poetry run tox -e lint

# Run type checking
poetry run tox -e type
```

## Documentation

Documentation is available in the `docs/` directory. To build the documentation:

```bash
# Install documentation dependencies
poetry install --with docs

# Build HTML documentation
poetry run sphinx-build -b html docs docs/_build
```

## Docker

### Building the Docker Image

```bash
docker build -t project-name:latest .
```

### Running the Container

```bash
docker run -it --rm project-name:latest
```

### Docker Compose

If you have a `docker-compose.yml`:

```bash
docker-compose up
```

## Environment Variables

Copy `.env.example` to `.env` and configure your environment variables:

```bash
cp .env.example .env
```

Key environment variables:

- `APP_ENV`: Application environment (development/staging/production)
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Logging level
- See `.env.example` for all available options

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow

1. Ensure all tests pass
2. Update documentation as needed
3. Add tests for new functionality
4. Ensure code passes all quality checks
5. Submit a pull request

## Troubleshooting

### Common Issues

**Issue**: Poetry installation fails

- **Solution**: Ensure you have Python 3.11+ and try using the official installer

**Issue**: Pre-commit hooks fail

- **Solution**: Run `pre-commit run --all-files` to see detailed errors

**Issue**: Tests fail locally

- **Solution**: Ensure all dependencies are installed with `poetry install --with dev`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- List any libraries, tools, or resources you want to acknowledge
- Contributors and maintainers
- Inspiration sources

## Contact

- **GitHub**: [@posgnu](https://github.com/posgnu)
- **Project Link**: [https://github.com/posgnu/gigr-mcp-server](https://github.com/posgnu/gigr-mcp-server)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes between versions.

---

Built with the [Model Context Protocol](https://modelcontextprotocol.io/) and [DuckDB](https://duckdb.org/)
