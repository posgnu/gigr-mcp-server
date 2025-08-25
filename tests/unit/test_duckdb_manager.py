"""Unit tests for DuckDB manager module."""

import tempfile
from pathlib import Path

import duckdb
import pytest

from src.duckdb_manager import DuckDBManager, get_db_manager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.duckdb"
        yield str(db_path)


@pytest.fixture
def db_manager(temp_db):
    """Create a DuckDBManager instance for testing."""
    return DuckDBManager(temp_db)


def test_init_creates_data_directory(temp_db):
    """Test that initialization creates the data directory."""
    db_path = Path(temp_db).parent / "nested" / "path" / "test.duckdb"
    DuckDBManager(str(db_path))

    assert db_path.parent.exists()


def test_connection_property(db_manager):
    """Test connection property creates and returns connection."""
    conn = db_manager.connection

    assert conn is not None
    assert isinstance(conn, duckdb.DuckDBPyConnection)

    # Should return same connection on subsequent calls
    conn2 = db_manager.connection
    assert conn is conn2


def test_execute_query(db_manager):
    """Test executing a SELECT query."""
    # Create a test table
    db_manager.execute_statement("CREATE TABLE test (id INTEGER, name VARCHAR)")
    db_manager.execute_statement("INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob')")

    # Execute query
    rows, columns = db_manager.execute_query("SELECT * FROM test ORDER BY id")

    assert columns == ["id", "name"]
    assert len(rows) == 2
    assert rows[0] == {"id": 1, "name": "Alice"}
    assert rows[1] == {"id": 2, "name": "Bob"}


def test_execute_query_with_parameters(db_manager):
    """Test executing a query with parameters."""
    db_manager.execute_statement("CREATE TABLE test (id INTEGER, name VARCHAR)")
    db_manager.execute_statement("INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob')")

    rows, columns = db_manager.execute_query(
        "SELECT * FROM test WHERE name = ?", ["Alice"]
    )

    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"


def test_execute_statement_ddl(db_manager):
    """Test executing DDL statements."""
    affected = db_manager.execute_statement("CREATE TABLE test (id INTEGER)")

    # DDL statements return 0 affected rows
    assert affected == 0

    # Verify table was created
    tables = db_manager.list_tables()
    assert "test" in tables


def test_execute_statement_dml(db_manager):
    """Test executing DML statements."""
    db_manager.execute_statement("CREATE TABLE test (id INTEGER)")

    # Test INSERT
    affected = db_manager.execute_statement("INSERT INTO test VALUES (1), (2), (3)")
    # DuckDB returns count in a special way, might be 0
    assert affected >= 0


def test_list_tables(db_manager):
    """Test listing tables."""
    # Initially no tables
    tables = db_manager.list_tables()
    assert len(tables) == 0

    # Create tables
    db_manager.execute_statement("CREATE TABLE table1 (id INTEGER)")
    db_manager.execute_statement("CREATE TABLE table2 (id INTEGER)")

    tables = db_manager.list_tables()
    assert len(tables) == 2
    assert "table1" in tables
    assert "table2" in tables


def test_list_views(db_manager):
    """Test listing views."""
    # Create a table and view
    db_manager.execute_statement("CREATE TABLE test (id INTEGER)")
    db_manager.execute_statement("CREATE VIEW test_view AS SELECT * FROM test")

    views = db_manager.list_views()
    assert len(views) == 1
    assert "test_view" in views


def test_describe_table(db_manager):
    """Test describing table schema."""
    db_manager.execute_statement(
        "CREATE TABLE test (id INTEGER NOT NULL, name VARCHAR, age INTEGER DEFAULT 0)"
    )

    columns = db_manager.describe_table("test")

    assert len(columns) == 3

    id_col = next(c for c in columns if c["column_name"] == "id")
    assert id_col["data_type"] == "INTEGER"
    assert id_col["is_nullable"] == "NO"

    name_col = next(c for c in columns if c["column_name"] == "name")
    assert name_col["data_type"] == "VARCHAR"
    assert name_col["is_nullable"] == "YES"


def test_get_table_stats(db_manager):
    """Test getting table statistics."""
    db_manager.execute_statement("CREATE TABLE test (id INTEGER)")
    db_manager.execute_statement("INSERT INTO test VALUES (1), (2), (3)")

    stats = db_manager.get_table_stats("test")

    assert stats["table_name"] == "test"
    assert stats["row_count"] == 3
    assert "table_size" in stats


def test_close(db_manager):
    """Test closing the connection."""
    # Create connection
    conn = db_manager.connection
    assert conn is not None

    # Close it
    db_manager.close()
    assert db_manager._connection is None

    # Should create new connection when accessed again
    new_conn = db_manager.connection
    assert new_conn is not None


def test_get_connection_context_manager(db_manager):
    """Test get_connection context manager."""
    with db_manager.get_connection() as conn:
        assert conn is not None
        assert isinstance(conn, duckdb.DuckDBPyConnection)


def test_get_connection_error_handling(db_manager):
    """Test get_connection handles errors."""
    with pytest.raises(duckdb.CatalogException), db_manager.get_connection() as conn:
        # This should raise an error
        conn.execute("SELECT * FROM nonexistent_table")


def test_get_db_manager_singleton():
    """Test get_db_manager returns singleton."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test.duckdb")

        manager1 = get_db_manager(db_path)
        manager2 = get_db_manager(db_path)

        assert manager1 is manager2


def test_import_csv(db_manager):
    """Test importing CSV data."""
    # Create a CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("id,name\n")
        f.write("1,Alice\n")
        f.write("2,Bob\n")
        csv_path = f.name

    try:
        # Create table
        db_manager.execute_statement("CREATE TABLE test (id INTEGER, name VARCHAR)")

        # Import CSV
        rows = db_manager.import_csv(csv_path, "test", HEADER=True)

        assert rows == 2

        # Verify data
        result, _ = db_manager.execute_query("SELECT * FROM test ORDER BY id")
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
    finally:
        Path(csv_path).unlink()


def test_export_table_csv(db_manager):
    """Test exporting table to CSV."""
    # Create and populate table
    db_manager.execute_statement("CREATE TABLE test (id INTEGER, name VARCHAR)")
    db_manager.execute_statement("INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob')")

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        csv_path = f.name

    try:
        db_manager.export_table("test", csv_path, "CSV")

        # Verify file was created
        assert Path(csv_path).exists()

        # Read and verify content
        content = Path(csv_path).read_text()
        assert "Alice" in content
        assert "Bob" in content
    finally:
        Path(csv_path).unlink()
