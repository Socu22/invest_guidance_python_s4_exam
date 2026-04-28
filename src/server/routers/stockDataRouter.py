from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from ..database.db import get_db_connection
from dotenv import load_dotenv
import os
import requests
import json

# Load environment variables
load_dotenv()
api_token = os.getenv("API_TOKEN")

# ----------------------
# MODELS
# ----------------------

class Stock(BaseModel):
    id: int
    ticker: str
    data: List[Dict[str, Any]]

class StockResponse(BaseModel):
    id: int
    ticker: str
    data: List[Dict[str, Any]]
    message: str  # Added message field for success/error messages

class StockCreate(BaseModel):
    ticker: str

class StockUpdate(BaseModel):
    ticker: str

# ----------------------
# ROUTER
# ----------------------

router = APIRouter(prefix="/stocks", tags=["stocks"])

# ----------------------
# ENDPOINTS
# ----------------------

@router.get("/{ticker}", response_model=Stock)
def get_stock(ticker: str):
    """Fetch stock data for a given ticker from the database."""
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute('SELECT data FROM stocks WHERE ticker = ?;', (ticker,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Stock not found")

        stock_data = json.loads(row[0])

        cursor.execute("SELECT id FROM stocks WHERE ticker = ?;", (ticker,))
        row = cursor.fetchone()
        stock_id = row[0] if row else 1

        return {"id": stock_id, "ticker": ticker, "data": stock_data}
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {err}")

@router.post("/", response_model=StockResponse, status_code=201)
def create_stock(stock: StockCreate):
    """Fetch stock data from EODHD API and create a new stock entry in the database."""
    ticker = stock.ticker
    url = f"https://eodhd.com/api/eod/{ticker}?api_token={api_token}&fmt=json"

    try:
        # Fetch data from EODHD API
        response = requests.get(url)
        response.raise_for_status()
        eod_data = response.json()

        # Ensure eod_data is a list
        if not isinstance(eod_data, list):
            eod_data = [eod_data]

        db = get_db_connection()
        cursor = db.cursor()

        # Check if the ticker already exists
        cursor.execute('SELECT 1 FROM stocks WHERE ticker = ?;', (ticker,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail=f"Stock {ticker} already exists. Use PUT /stocks/ to update."
            )

        # Insert new stock data
        cursor.execute('''
            INSERT INTO stocks (ticker, data) VALUES (?, ?);
        ''', (ticker, json.dumps(eod_data)))

        db.commit()

        # Fetch the newly inserted ID
        cursor.execute("SELECT id FROM stocks WHERE ticker = ?;", (ticker,))
        row = cursor.fetchone()
        stock_id = row[0] if row else 1

        return {
            "id": stock_id,
            "ticker": ticker,
            "data": eod_data,
            "message": f"Stock {ticker} created successfully."
        }

    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail=f"Failed to fetch EOD data: {err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error creating stock: {err}")

@router.put("/", response_model=StockResponse)
def update_stock(stock: StockUpdate):
    """Fetch stock data from EODHD API and update the existing stock entry in the database."""
    ticker = stock.ticker
    url = f"https://eodhd.com/api/eod/{ticker}?api_token={api_token}&fmt=json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        new_data = response.json()

        if not isinstance(new_data, list):
            new_data = [new_data]

        db = get_db_connection()
        cursor = db.cursor()

        # Fetch existing data
        cursor.execute('SELECT data FROM stocks WHERE ticker = ?;', (ticker,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Stock {ticker} not found. Use POST /stocks/ to create a new entry."
            )

        existing_data = json.loads(row[0])
        existing_dates = {item["date"] for item in existing_data}

        # Append new data that doesn't already exist
        updated_data = existing_data.copy()
        new_dates = 0
        for item in new_data:
            if item["date"] not in existing_dates:
                updated_data.append(item)
                new_dates += 1

        # Sort the combined data by date (oldest to newest)
        updated_data.sort(key=lambda x: x["date"])

        # Update the stock data
        cursor.execute('''
            UPDATE stocks SET data = ? WHERE ticker = ?;
        ''', (json.dumps(updated_data), ticker))

        db.commit()

        cursor.execute("SELECT id FROM stocks WHERE ticker = ?;", (ticker,))
        row = cursor.fetchone()
        stock_id = row[0] if row else 1

        message = f"Stock {ticker} updated successfully."
        if new_dates > 0:
            message += f" Added {new_dates} new entries."
        else:
            message += " No new data to add."

        return {
            "id": stock_id,
            "ticker": ticker,
            "data": updated_data,
            "message": message
        }

    except requests.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail=f"Failed to fetch EOD data: {err}")
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating stock: {err}")