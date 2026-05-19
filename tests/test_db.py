import pytest
import sqlite3
import json
from pathlib import Path
from server.database.db import (
    get_db_connection,
    close_db_connection,
    initialize_stock_database,
    _db_connection
)

# Database path for testing
TEST_DB_PATH = str(Path(__file__).parent.parent / "stockDataDatabase.db")

@pytest.fixture(scope="module")
def test_db():
    """Fixture to set up and tear down a test database"""
    print("\n=== SETUP: Initializing test database for DB tests ===")
    initialize_stock_database(delete_mode=True)  # Start fresh
    print("=== SETUP: Database initialized with AAPL data ===")

    yield

    print("\n=== TEARDOWN: Cleaning up test database ===")
    close_db_connection()
    if Path(TEST_DB_PATH).exists():
        print(f"=== TEARDOWN: Removing test database file at {TEST_DB_PATH} ===")
        Path(TEST_DB_PATH).unlink()
    print("=== TEARDOWN: Cleanup complete ===\n")

def test_get_db_connection(test_db):
    """Test get_db_connection function"""
    print("\n--- TEST: get_db_connection() ---")
    conn = get_db_connection()
    print(f"Connection type: {type(conn)}")
    print(f"Connection object: {conn}")

    assert conn is not None
    print("✓ Connection is not None")
    assert isinstance(conn, sqlite3.Connection)
    print("✓ Connection is a SQLite connection")
    print("--- TEST PASSED ---")

def test_close_db_connection(test_db):
    """Test close_db_connection function"""
    print("\n--- TEST: close_db_connection() ---")
    # Ensure a connection exists
    conn = get_db_connection()
    print(f"Initial connection: {conn}")
    assert conn is not None
    print("✓ Connection exists before closing")

    # Close it
    close_db_connection()
    print("✓ Connection closed")

    # Verify it's closed
    assert _db_connection is None
    print("✓ Global connection is None after closing")
    print("--- TEST PASSED ---")

def test_initialize_stock_database(test_db):
    """Test initialize_stock_database function"""
    print("\n--- TEST: initialize_stock_database() ---")

    # Initialize the database
    initialize_stock_database()
    print("✓ Database initialized")

    # Get a cursor to check the results
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stocks';")
    table_exists = cursor.fetchone()
    print(f"Table exists check: {table_exists}")
    assert table_exists is not None
    print("✓ Stocks table exists")

    # Check if AAPL data was inserted
    cursor.execute("SELECT ticker, data FROM stocks WHERE ticker='AAPL';")
    row = cursor.fetchone()
    print(f"AAPL row: {row}")
    assert row is not None
    print("✓ AAPL row exists")

    assert row["ticker"] == "AAPL"
    print(f"✓ Ticker matches: {row['ticker']}")

    data = json.loads(row["data"])
    print(f"AAPL data: {data}")
    assert len(data) == 3  # 3 entries for AAPL
    print(f"✓ AAPL has {len(data)} entries")

    assert data[0]["date"] == "2026-04-22"
    print(f"✓ First entry date: {data[0]['date']}")
    print("--- TEST PASSED ---")

def test_initialize_stock_database_delete_mode(test_db):
    """Test initialize_stock_database with delete_mode=True"""
    print("\n--- TEST: initialize_stock_database(delete_mode=True) ---")

    # Initialize the database
    initialize_stock_database()
    print("✓ Database initialized")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stocks';")
    assert cursor.fetchone() is not None
    print("✓ Stocks table exists before deletion")

    # Re-initialize with delete_mode=True
    initialize_stock_database(delete_mode=True)
    print("✓ Database re-initialized with delete_mode=True")

    # Verify the table is dropped
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stocks';")
    table_exists = cursor.fetchone()
    print(f"Table exists after deletion: {table_exists}")
    assert table_exists is None
    print("✓ Stocks table successfully dropped")
    print("--- TEST PASSED ---")