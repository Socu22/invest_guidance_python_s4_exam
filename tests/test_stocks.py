import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import sqlite3
from pathlib import Path
from server.app import app
from server.database.db import get_db_connection, close_db_connection, initialize_stock_database

client = TestClient(app)

# Sample stock data for mocking API responses
SAMPLE_STOCK_DATA = [
    {"date": "2026-05-19", "open": 100.0, "close": 105.0, "high": 110.0, "low": 95.0, "volume": 1000000},
    {"date": "2026-05-20", "open": 105.0, "close": 110.0, "high": 115.0, "low": 100.0, "volume": 1200000}
]

@pytest.fixture(scope="module")
def test_db():
    """Fixture to set up and tear down a test database"""
    print("\n=== SETUP: Initializing test database ===")
    initialize_stock_database(delete_mode=True)  # Start fresh
    print("=== SETUP: Database initialized with AAPL data ===")

    yield

    print("\n=== TEARDOWN: Cleaning up test database ===")
    close_db_connection()
    db_path = Path(__file__).parent.parent / "stockDataDatabase.db"
    if db_path.exists():
        print(f"=== TEARDOWN: Removing test database file at {db_path} ===")
        db_path.unlink()
    print("=== TEARDOWN: Cleanup complete ===\n")

def test_get_all_stocks_success(test_db):
    """Test GET /stocks/ with existing data"""
    print("\n--- TEST: GET /stocks/ (success) ---")
    response = client.get("/stocks/")
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"Found {len(data)} stocks in database")

    # Should have the AAPL data from initialization
    assert any(stock["ticker"] == "AAPL" for stock in data)
    print("✓ AAPL stock found in results")
    print("--- TEST PASSED ---")

def test_get_stock_success(test_db):
    """Test GET /stocks/{ticker} with existing stock"""
    print("\n--- TEST: GET /stocks/AAPL (success) ---")
    response = client.get("/stocks/AAPL")
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    print(f"✓ Ticker matches: {data['ticker']}")

    assert len(data["data"]) == 3  # From initialization
    print(f"✓ Stock data has {len(data['data'])} entries")

    assert data["id"] == 1
    print(f"✓ Stock ID: {data['id']}")
    print("--- TEST PASSED ---")

@patch("server.routers.stockDataRouter.httpx.AsyncClient")
def test_create_stock_success(mock_async_client, test_db):
    """Test POST /stocks/ with new stock"""
    print("\n--- TEST: POST /stocks/ (create GOOGL) ---")

    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_STOCK_DATA
    mock_response.raise_for_status.return_value = None
    mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response
    print("✓ Mocked EODHD API response with sample data")

    response = client.post("/stocks/", json={"ticker": "GOOGL"})
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.json()}")

    assert response.status_code == 201
    data = response.json()
    assert data["ticker"] == "GOOGL"
    print(f"✓ Created stock: {data['ticker']}")

    assert "created successfully" in data["message"]
    print(f"✓ Success message: {data['message']}")

    assert len(data["data"]) == 2  # Our sample data has 2 entries
    print(f"✓ Stock data has {len(data['data'])} entries")
    print("--- TEST PASSED ---")

@patch("server.routers.stockDataRouter.httpx.AsyncClient")
def test_update_stock_success(mock_async_client, test_db):
    """Test PUT /stocks/ with existing stock"""
    print("\n--- TEST: PUT /stocks/AAPL (update) ---")

    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_STOCK_DATA
    mock_response.raise_for_status.return_value = None
    mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response
    print("✓ Mocked EODHD API response with sample data")

    response = client.put("/stocks/", json={"ticker": "AAPL"})
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    print(f"✓ Updated stock: {data['ticker']}")

    assert "updated successfully" in data["message"]
    print(f"✓ Success message: {data['message']}")

    # Should have original 3 entries + 2 new ones (but dates might overlap)
    assert len(data["data"]) >= 3  # At least the original 3 entries
    print(f"✓ Stock now has {len(data['data'])} entries (original + new)")
    print("--- TEST PASSED ---")