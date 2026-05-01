import sqlite3
import sys
import json

# Global variable to hold the SQLite connection
_db_connection = None

def get_db_connection() -> sqlite3.Connection:
    """Return a singleton SQLite connection."""
    global _db_connection
    if _db_connection is None:
        _db_connection = sqlite3.connect('stockDataDatabase.db', check_same_thread=False)
        _db_connection.row_factory = sqlite3.Row  # For named columns
        _db_connection.execute("PRAGMA journal_mode=WAL;")  # For concurrency
        # Verify WAL mode is enabled
        cursor = _db_connection.cursor()
        cursor.execute("PRAGMA journal_mode;")
        print(f"Journal mode: {cursor.fetchone()[0]}")  # Should print 'wal'
        print("Database connection opened.")
    return _db_connection

def close_db_connection() -> None:
    """Close the global database connection."""
    global _db_connection
    if _db_connection is not None:
        _db_connection.close()
        _db_connection = None
        print("Database connection closed.")
    else:
        print("Database connection already closed.")

def initialize_stock_database(delete_mode=False):
    """Initialize the SQLite database with a table for stock tickers and JSON data."""
    db = get_db_connection()  # Use the singleton connection
    cursor = db.cursor()

    try:
        if delete_mode:
            cursor.execute('DROP TABLE IF EXISTS stocks;')
            print("Stocks table dropped.")

        # Create the stocks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE,
                data TEXT NOT NULL  -- Store JSON as text
            );
        ''')
        print("Stocks table created or already exists.")

        # Example data for AAPL (Apple)
        aapl_data = [
            {
                "date": "2026-04-22",
                "open": 252.44,
                "high": 255.94,
                "low": 250.33,  # Fixed typo
                "close": 255.36,
                "adjusted_close": 255.36,
                "volume": 36065100
            },
            {
                "date": "2026-04-23",
                "open": 255.39,
                "high": 258.79,
                "low": 253.07,  # Fixed typo
                "close": 255.08,
                "adjusted_close": 255.08,
                "volume": 39091400
            },
            {
                "date": "2026-04-24",
                "open": 259.98,
                "high": 264.50,
                "low": 257.69,
                "close": 263.99,
                "adjusted_close": 263.99,
                "volume": 53777400
            },
        ]

        # Insert data as text
        cursor.execute('''
            INSERT OR REPLACE INTO stocks (ticker, data)
            VALUES (?, ?);
        ''', ("AAPL", json.dumps(aapl_data)))

        db.commit()
        print("Stock database initialized successfully with AAPL data as text.")

    except Exception as err:
        print(f"Error initializing stock database: {err}")
        db.rollback()
        raise err

if __name__ == "__main__":
    delete_mode = "--delete" in sys.argv
    initialize_stock_database(delete_mode)