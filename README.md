# GIGR MCP Server

A Model Context Protocol (MCP) server with DuckDB integration, providing AI
models with direct access to a DuckDB database.

## Installation

```bash
# Clone and install
git clone https://github.com/posgnu/gigr-mcp-server.git
cd gigr-db-mcp
poetry install
```

## Running the Server

```bash
# Run the MCP server using the CLI command
poetry run gigr-mcp-server
```

## Supported Protocols

This server uses **stdio** (standard input/output) transport protocol. HTTP
transport is **not supported**.

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector poetry run python -m src.main
```

Opens a web interface to test all tools and inspect request/response payloads.

## Available Tools

### Query Execution

- `execute_query` - Execute SELECT queries with JSON output
- `execute_statement` - Execute DDL/DML statements (CREATE, INSERT, UPDATE, DELETE)

### Schema Inspection

- `list_tables` - Get all tables in the database
- `list_views` - Get all views in the database
- `describe_table` - Get table schema with column details
- `get_table_stats` - Get table statistics (row count, size)

### Data Import/Export

- `import_csv` - Import CSV file into a table
- `export_table` - Export table to CSV or Parquet format

### Resources

- `duckdb://status` - Current database status
- `duckdb://schema` - Complete database schema

## Claude Desktop Configuration

Add to your Claude Desktop config file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

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

Restart Claude Desktop after updating the configuration.

## Database Details

- **Database Path**: `./data/gigr.duckdb`
- **Auto-creation**: Database and data directory created automatically
- **Features**: SQL injection prevention, transaction support, query timeout
