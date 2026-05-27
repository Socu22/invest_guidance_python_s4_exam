import sqlite3
import sys
import json
from pathlib import Path
import os

# Global variable to hold the SQLite connection
_db_connection = None


def get_db_connection() -> sqlite3.Connection:
    """Return a singleton SQLite connection."""
    global _db_connection
    if _db_connection is None:

        # DEFAULT path
        db_path = Path(__file__).parent.parent / "stockDataDatabase.db"

        env_db_path = os.getenv("DB_PATH")
        if env_db_path:
            db_path = Path(env_db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)

        _db_connection = sqlite3.connect(str(db_path), check_same_thread=False)
        _db_connection.row_factory = sqlite3.Row  # For named columns

        _db_connection.execute("PRAGMA journal_mode=WAL;")
        _db_connection.execute("PRAGMA synchronous=NORMAL;")
        _db_connection.execute("PRAGMA busy_timeout=5000;")

        cursor = _db_connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL UNIQUE,
            data TEXT NOT NULL
        );
        """)
        _db_connection.commit()
        cursor.execute("PRAGMA journal_mode;")

        print(f"Journal mode: {cursor.fetchone()[0]}")
        print("Database connection opened.")
        print("[DB PATH]", db_path)
        print("[CONN ID]", id(_db_connection))

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
    db = get_db_connection()
    cursor = db.cursor()

    try:
        if delete_mode:
            cursor.execute('DROP TABLE IF EXISTS stocks;')
            print("Stocks table dropped.")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE,
                data TEXT NOT NULL
            );
        ''')

        print("Stocks table created or already exists.")

        aapl_data = [
            {
                "date": "2026-04-22",
                "open": 252.44,
                "high": 255.94,
                "low": 250.33,
                "close": 255.36,
                "adjusted_close": 255.36,
                "volume": 36065100
            },
            {
                "date": "2026-04-23",
                "open": 255.39,
                "high": 258.79,
                "low": 253.07,
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

    delete_docker_mode = os.getenv("DELETE_DB", "false").lower() == "true"

    
    # Docker has priority
    initialize_stock_database(delete_docker_mode or delete_mode)

        
