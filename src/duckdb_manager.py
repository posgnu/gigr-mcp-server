"""DuckDB connection manager for MCP server."""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import duckdb

from .logger import get_logger

logger = get_logger(__name__)


class DuckDBManager:
    """Manages DuckDB database connections and operations."""

    def __init__(self, db_path: str = "./data/gigr.duckdb"):
        """Initialize DuckDB manager.

        Args:
            db_path: Path to the DuckDB database file
        """
        self.db_path = db_path
        self._connection: duckdb.DuckDBPyConnection | None = None
        self._ensure_data_directory()

    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists."""
        data_dir = Path(self.db_path).parent
        data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data directory ensured at: {data_dir}")

    @property
    def connection(self) -> duckdb.DuckDBPyConnection:
        """Get or create the database connection.

        Returns:
            Active DuckDB connection
        """
        if self._connection is None:
            self._connection = duckdb.connect(self.db_path)
            logger.info(f"Connected to DuckDB at: {self.db_path}")
        return self._connection

    @contextmanager
    def get_connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        """Context manager for database connection.

        Yields:
            DuckDB connection
        """
        try:
            yield self.connection
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            raise

    def execute_query(
        self, query: str, parameters: list[Any] | None = None
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """Execute a SELECT query and return results.

        Args:
            query: SQL query to execute
            parameters: Optional query parameters

        Returns:
            Tuple of (rows as list of dicts, column names)
        """
        with self.get_connection() as conn:
            try:
                if parameters is not None:
                    result = conn.execute(query, parameters)
                else:
                    result = conn.execute(query)

                # Get column names
                columns = (
                    [desc[0] for desc in result.description]
                    if result.description
                    else []
                )

                # Fetch all rows
                rows = result.fetchall()

                # Convert to list of dicts
                dict_rows = [dict(zip(columns, row, strict=False)) for row in rows]

                logger.info(
                    f"Query executed successfully, returned {len(dict_rows)} rows"
                )
                return dict_rows, columns

            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise

    def execute_statement(
        self, statement: str, parameters: list[Any] | None = None
    ) -> int:
        """Execute a DDL/DML statement.

        Args:
            statement: SQL statement to execute
            parameters: Optional statement parameters

        Returns:
            Number of affected rows (0 for DDL statements)
        """
        with self.get_connection() as conn:
            try:
                if parameters is not None:
                    result = conn.execute(statement, parameters)
                else:
                    result = conn.execute(statement)

                # Try to get affected rows count
                # DDL statements (CREATE, DROP, ALTER) don't have row counts
                # DML statements (INSERT, UPDATE, DELETE) do
                try:
                    # For DML statements, DuckDB returns the count
                    row = result.fetchone()
                    if row is not None:
                        affected_rows = row[0] if isinstance(row[0], int) else 0
                    else:
                        affected_rows = 0
                except Exception:
                    # DDL statements or statements without results
                    affected_rows = 0

                logger.info(
                    f"Statement executed successfully, {affected_rows} rows affected"
                )
                return affected_rows

            except Exception as e:
                logger.error(f"Statement execution failed: {e}")
                raise

    def list_tables(self) -> list[str]:
        """Get list of all tables in the database.

        Returns:
            List of table names
        """
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        rows, _ = self.execute_query(query)
        return [row["table_name"] for row in rows]

    def list_views(self) -> list[str]:
        """Get list of all views in the database.

        Returns:
            List of view names
        """
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
        AND table_type = 'VIEW'
        ORDER BY table_name
        """
        rows, _ = self.execute_query(query)
        return [row["table_name"] for row in rows]

    def describe_table(self, table_name: str) -> list[dict[str, Any]]:
        """Get table schema information.

        Args:
            table_name: Name of the table to describe

        Returns:
            List of column information dictionaries
        """
        query = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'main'
        AND table_name = ?
        ORDER BY ordinal_position
        """
        rows, _ = self.execute_query(query, [table_name])
        return rows

    def get_table_stats(self, table_name: str) -> dict[str, Any]:
        """Get table statistics.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary with table statistics
        """
        try:
            # Get row count
            count_query = (
                f"SELECT COUNT(*) as row_count FROM {table_name}"  # nosec B608
            )
            rows, _ = self.execute_query(count_query)
            row_count = rows[0]["row_count"] if rows else 0

            # Get table size (approximate)
            size_query = f"""
            SELECT
                pg_size_pretty(pg_relation_size('{table_name}')) as table_size
            """
            try:
                size_rows, _ = self.execute_query(size_query)
                table_size = size_rows[0]["table_size"] if size_rows else "N/A"
            except Exception:
                table_size = "N/A"

            return {
                "table_name": table_name,
                "row_count": row_count,
                "table_size": table_size,
            }
        except Exception as e:
            logger.error(f"Failed to get stats for table {table_name}: {e}")
            raise

    def import_csv(self, file_path: str, table_name: str, **options: Any) -> int:
        """Import CSV file into a table.

        Args:
            file_path: Path to CSV file
            table_name: Target table name
            **options: Additional CSV import options

        Returns:
            Number of rows imported
        """
        with self.get_connection() as conn:
            try:
                # Build options string
                csv_options = []
                for k, v in options.items():
                    if k.upper() == "HEADER" and v:
                        csv_options.append("HEADER")
                    elif k.upper() == "DELIMITER":
                        csv_options.append(f"DELIMITER {v}")
                    else:
                        csv_options.append(f"{k} {v}")

                option_str = ", ".join(csv_options) if csv_options else "HEADER"
                query = (
                    f"COPY {table_name} FROM '{file_path}' (FORMAT CSV, {option_str})"
                )

                conn.execute(query)

                # Get row count
                count_query = f"SELECT COUNT(*) FROM {table_name}"  # nosec B608
                result = conn.execute(count_query)
                row_result = result.fetchone()
                row_count = row_result[0] if row_result else 0

                logger.info(
                    f"Imported {row_count} rows from {file_path} to {table_name}"
                )
                return row_count

            except Exception as e:
                logger.error(f"CSV import failed: {e}")
                raise

    def export_table(
        self, table_name: str, file_path: str, format: str = "CSV"
    ) -> None:
        """Export table to file.

        Args:
            table_name: Table to export
            file_path: Output file path
            format: Export format (CSV or PARQUET)
        """
        with self.get_connection() as conn:
            try:
                if format.upper() == "CSV":
                    query = f"COPY {table_name} TO '{file_path}' (FORMAT CSV, HEADER)"
                elif format.upper() == "PARQUET":
                    query = f"COPY {table_name} TO '{file_path}' (FORMAT PARQUET)"
                else:
                    raise ValueError(f"Unsupported format: {format}")

                conn.execute(query)
                logger.info(f"Exported {table_name} to {file_path} as {format}")

            except Exception as e:
                logger.error(f"Export failed: {e}")
                raise

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")


# Global instance
_db_manager: DuckDBManager | None = None


def get_db_manager(db_path: str = "./data/gigr.duckdb") -> DuckDBManager:
    """Get or create the global DuckDB manager instance.

    Args:
        db_path: Path to the database file

    Returns:
        DuckDBManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DuckDBManager(db_path)
    return _db_manager
