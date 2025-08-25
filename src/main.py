"""GIGR MCP Server - Model Context Protocol server with DuckDB support."""

import json
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .duckdb_manager import get_db_manager
from .logger import setup_logger

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE")
logger = setup_logger(
    __name__, level=log_level, log_file=Path(log_file) if log_file else None
)

# Create MCP server instance
mcp = FastMCP("GIGR DuckDB MCP Server")

# Initialize DuckDB manager
db = get_db_manager()


@mcp.tool()  # type: ignore[misc]
def execute_query(query: str, parameters: list[Any] | None = None) -> dict[str, Any]:
    """Execute a SELECT query on the DuckDB database.

    Args:
        query: SQL SELECT query to execute
        parameters: Optional list of query parameters for prepared statements

    Returns:
        Dictionary with query results including columns, rows, and metadata
    """
    try:
        rows, columns = db.execute_query(query, parameters)

        # Create structured output
        result = {
            "success": True,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "query": query,
        }

        # Also create text representation for backwards compatibility
        text_lines = [f"Query executed successfully. Returned {len(rows)} rows."]
        if rows:
            text_lines.append(f"Columns: {', '.join(columns)}")
            text_lines.append("First 5 rows:")
            for i, row in enumerate(rows[:5]):
                text_lines.append(f"  Row {i+1}: {json.dumps(row, default=str)}")

        result["text"] = "\n".join(text_lines)
        return result

    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "text": f"Query failed: {str(e)}",
        }


@mcp.tool()  # type: ignore[misc]
def execute_statement(
    statement: str, parameters: list[Any] | None = None
) -> dict[str, Any]:
    """Execute a DDL/DML statement (CREATE, INSERT, UPDATE, DELETE).

    Args:
        statement: SQL statement to execute
        parameters: Optional list of statement parameters

    Returns:
        Dictionary with execution result and affected rows
    """
    try:
        affected_rows = db.execute_statement(statement, parameters)

        return {
            "success": True,
            "affected_rows": affected_rows,
            "statement": statement,
            "text": f"Statement executed successfully. {affected_rows} rows affected.",
        }

    except Exception as e:
        logger.error(f"Statement execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "statement": statement,
            "text": f"Statement failed: {str(e)}",
        }


@mcp.tool()  # type: ignore[misc]
def list_tables() -> dict[str, Any]:
    """List all tables in the DuckDB database.

    Returns:
        Dictionary with list of table names
    """
    try:
        tables = db.list_tables()

        return {
            "success": True,
            "tables": tables,
            "count": len(tables),
            "text": (
                f"Found {len(tables)} tables: "
                f"{', '.join(tables) if tables else 'none'}"
            ),
        }

    except Exception as e:
        logger.error(f"Failed to list tables: {e}")
        return {
            "success": False,
            "error": str(e),
            "text": f"Failed to list tables: {str(e)}",
        }


@mcp.tool()  # type: ignore[misc]
def list_views() -> dict[str, Any]:
    """List all views in the DuckDB database.

    Returns:
        Dictionary with list of view names
    """
    try:
        views = db.list_views()

        return {
            "success": True,
            "views": views,
            "count": len(views),
            "text": (
                f"Found {len(views)} views: " f"{', '.join(views) if views else 'none'}"
            ),
        }

    except Exception as e:
        logger.error(f"Failed to list views: {e}")
        return {
            "success": False,
            "error": str(e),
            "text": f"Failed to list views: {str(e)}",
        }


@mcp.tool()  # type: ignore[misc]
def describe_table(table_name: str) -> dict[str, Any]:
    """Get schema information for a specific table.

    Args:
        table_name: Name of the table to describe

    Returns:
        Dictionary with table schema information
    """
    try:
        columns = db.describe_table(table_name)

        # Format text output
        text_lines = [f"Table: {table_name}"]
        text_lines.append(f"Columns ({len(columns)}):")
        for col in columns:
            nullable = "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
            default = (
                f" DEFAULT {col['column_default']}" if col["column_default"] else ""
            )
            text_lines.append(
                f"  - {col['column_name']}: {col['data_type']} {nullable}{default}"
            )

        return {
            "success": True,
            "table_name": table_name,
            "columns": columns,
            "column_count": len(columns),
            "text": "\n".join(text_lines),
        }

    except Exception as e:
        logger.error(f"Failed to describe table {table_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "text": f"Failed to describe table: {str(e)}",
        }


@mcp.tool()  # type: ignore[misc]
def get_table_stats(table_name: str) -> dict[str, Any]:
    """Get statistics for a specific table.

    Args:
        table_name: Name of the table

    Returns:
        Dictionary with table statistics
    """
    try:
        stats = db.get_table_stats(table_name)

        text = (
            f"Table: {stats['table_name']}\n"
            f"Row count: {stats['row_count']:,}\n"
            f"Size: {stats['table_size']}"
        )

        return {"success": True, **stats, "text": text}

    except Exception as e:
        logger.error(f"Failed to get stats for table {table_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "text": f"Failed to get table stats: {str(e)}",
        }


@mcp.tool()  # type: ignore[misc]
def import_csv(
    file_path: str,
    table_name: str,
    header: bool = True,
    delimiter: str = ",",
) -> dict[str, Any]:
    """Import a CSV file into a DuckDB table.

    Args:
        file_path: Path to the CSV file
        table_name: Name of the target table
        header: Whether the CSV has a header row
        delimiter: CSV delimiter character

    Returns:
        Dictionary with import result
    """
    try:
        options = {"HEADER": header, "DELIMITER": delimiter}

        row_count = db.import_csv(file_path, table_name, **options)

        return {
            "success": True,
            "table_name": table_name,
            "file_path": file_path,
            "rows_imported": row_count,
            "text": (
                f"Successfully imported {row_count:,} rows "
                f"from {file_path} into {table_name}"
            ),
        }

    except Exception as e:
        logger.error(f"Failed to import CSV: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "table_name": table_name,
            "text": f"Failed to import CSV: {str(e)}",
        }


@mcp.tool()  # type: ignore[misc]
def export_table(
    table_name: str, file_path: str, format: str = "CSV"
) -> dict[str, Any]:
    """Export a table to a file.

    Args:
        table_name: Name of the table to export
        file_path: Output file path
        format: Export format (CSV or PARQUET)

    Returns:
        Dictionary with export result
    """
    try:
        db.export_table(table_name, file_path, format)

        return {
            "success": True,
            "table_name": table_name,
            "file_path": file_path,
            "format": format,
            "text": f"Successfully exported {table_name} to {file_path} as {format}",
        }

    except Exception as e:
        logger.error(f"Failed to export table: {e}")
        return {
            "success": False,
            "error": str(e),
            "table_name": table_name,
            "file_path": file_path,
            "text": f"Failed to export table: {str(e)}",
        }


@mcp.resource("duckdb://status")  # type: ignore[misc]
def database_status() -> str:
    """Get the current database status and statistics.

    Returns:
        Database status information
    """
    try:
        tables = db.list_tables()
        views = db.list_views()

        status_lines = [
            "DuckDB Database Status",
            "=" * 40,
            f"Database path: {db.db_path}",
            f"Tables: {len(tables)}",
            f"Views: {len(views)}",
        ]

        if tables:
            status_lines.append("\nTables:")
            for table in tables[:10]:  # Show first 10 tables
                try:
                    stats = db.get_table_stats(table)
                    status_lines.append(f"  - {table}: {stats['row_count']:,} rows")
                except Exception:
                    status_lines.append(f"  - {table}")

        return "\n".join(status_lines)

    except Exception as e:
        return f"Failed to get database status: {str(e)}"


@mcp.resource("duckdb://schema")  # type: ignore[misc]
def database_schema() -> str:
    """Get the complete database schema.

    Returns:
        Database schema information
    """
    try:
        tables = db.list_tables()
        schema_lines = ["Database Schema", "=" * 40]

        for table in tables:
            try:
                columns = db.describe_table(table)
                schema_lines.append(f"\nTable: {table}")
                for col in columns:
                    nullable = "" if col["is_nullable"] == "YES" else " NOT NULL"
                    schema_lines.append(
                        f"  - {col['column_name']}: {col['data_type']}{nullable}"
                    )
            except Exception:
                schema_lines.append(f"\nTable: {table} (error reading schema)")

        return "\n".join(schema_lines)

    except Exception as e:
        return f"Failed to get database schema: {str(e)}"


def main() -> None:
    """Main function to run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
