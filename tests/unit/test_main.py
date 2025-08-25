"""Unit tests for main module."""

from unittest.mock import patch

from src.main import (
    describe_table,
    execute_query,
    execute_statement,
    export_table,
    get_table_stats,
    import_csv,
    list_tables,
    list_views,
    mcp,
)


def test_mcp_server_exists():
    """Test that MCP server is initialized."""
    assert mcp is not None
    assert mcp.name == "GIGR DuckDB MCP Server"


@patch("src.main.db")
def test_execute_query(mock_db):
    """Test execute_query function."""
    mock_db.execute_query.return_value = (
        [{"id": 1, "name": "test"}],
        ["id", "name"],
    )

    result = execute_query("SELECT * FROM test")

    assert result["success"] is True
    assert result["row_count"] == 1
    assert result["columns"] == ["id", "name"]
    assert result["rows"] == [{"id": 1, "name": "test"}]


@patch("src.main.db")
def test_execute_query_error(mock_db):
    """Test execute_query with error."""
    mock_db.execute_query.side_effect = Exception("Database error")

    result = execute_query("SELECT * FROM test")

    assert result["success"] is False
    assert "Database error" in result["error"]


@patch("src.main.db")
def test_execute_statement(mock_db):
    """Test execute_statement function."""
    mock_db.execute_statement.return_value = 5

    result = execute_statement("INSERT INTO test VALUES (1, 'test')")

    assert result["success"] is True
    assert result["affected_rows"] == 5


@patch("src.main.db")
def test_list_tables(mock_db):
    """Test list_tables function."""
    mock_db.list_tables.return_value = ["table1", "table2"]

    result = list_tables()

    assert result["success"] is True
    assert result["count"] == 2
    assert result["tables"] == ["table1", "table2"]


@patch("src.main.db")
def test_list_views(mock_db):
    """Test list_views function."""
    mock_db.list_views.return_value = ["view1", "view2"]

    result = list_views()

    assert result["success"] is True
    assert result["count"] == 2
    assert result["views"] == ["view1", "view2"]


@patch("src.main.db")
def test_describe_table(mock_db):
    """Test describe_table function."""
    mock_db.describe_table.return_value = [
        {
            "column_name": "id",
            "data_type": "INTEGER",
            "is_nullable": "NO",
            "column_default": None,
        },
        {
            "column_name": "name",
            "data_type": "VARCHAR",
            "is_nullable": "YES",
            "column_default": None,
        },
    ]

    result = describe_table("test_table")

    assert result["success"] is True
    assert result["column_count"] == 2
    assert result["table_name"] == "test_table"


@patch("src.main.db")
def test_get_table_stats(mock_db):
    """Test get_table_stats function."""
    mock_db.get_table_stats.return_value = {
        "table_name": "test_table",
        "row_count": 1000,
        "table_size": "1 MB",
    }

    result = get_table_stats("test_table")

    assert result["success"] is True
    assert result["row_count"] == 1000
    assert result["table_size"] == "1 MB"


@patch("src.main.db")
def test_import_csv(mock_db):
    """Test import_csv function."""
    mock_db.import_csv.return_value = 100

    result = import_csv("/path/to/file.csv", "test_table")

    assert result["success"] is True
    assert result["rows_imported"] == 100


@patch("src.main.db")
def test_export_table(mock_db):
    """Test export_table function."""
    mock_db.export_table.return_value = None

    result = export_table("test_table", "/path/to/output.csv")

    assert result["success"] is True
    assert result["format"] == "CSV"


@patch("src.main.db")
def test_database_status(mock_db):
    """Test database_status resource function."""
    from src.main import database_status

    mock_db.list_tables.return_value = ["table1", "table2"]
    mock_db.list_views.return_value = ["view1"]
    mock_db.get_table_stats.return_value = {"row_count": 100, "table_size": "1 MB"}

    result = database_status()

    assert "DuckDB Database Status" in result
    assert "Tables: 2" in result
    assert "Views: 1" in result


@patch("src.main.db")
def test_database_schema(mock_db):
    """Test database_schema resource function."""
    from src.main import database_schema

    mock_db.list_tables.return_value = ["table1"]
    mock_db.describe_table.return_value = [
        {
            "column_name": "id",
            "data_type": "INTEGER",
            "is_nullable": "NO",
            "column_default": None,
        }
    ]

    result = database_schema()

    assert "Database Schema" in result
    assert "Table: table1" in result
    assert "id: INTEGER NOT NULL" in result


@patch("src.main.db")
def test_error_handling_in_resources(mock_db):
    """Test error handling in resource functions."""
    from src.main import database_schema, database_status

    # Test database_status error
    mock_db.list_tables.side_effect = Exception("DB error")
    result = database_status()
    assert "Failed to get database status" in result

    # Test database_schema error
    mock_db.list_tables.side_effect = Exception("DB error")
    result = database_schema()
    assert "Failed to get database schema" in result


def test_main_function_exists():
    """Test that main function exists."""
    from src.main import main

    assert main is not None
    assert callable(main)
