from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ..database.db import get_db_connection
from dotenv import load_dotenv
import os
import httpx
import json

# ----------------------
# ENV SETUP
# ----------------------

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
    message: str

class StockCreate(BaseModel):
    ticker: str

class StockUpdate(BaseModel):
    ticker: str

# ----------------------
# ROUTER SETUP
# ----------------------

router = APIRouter(prefix="/stocks", tags=["stocks"])

# ----------------------
# ENDPOINTS
# ----------------------

@router.get("/", response_model=List[Stock])
async def get_all_stocks():
    """Fetch all stocks from the database."""
    try:
        # Connect to database
        db = get_db_connection()
        cursor = db.cursor()

        # Fetch all stocks
        cursor.execute('SELECT id, ticker, data FROM stocks;')
        rows = cursor.fetchall()

        # If no stocks exist
        if not rows:
            raise HTTPException(status_code=404, detail="No stocks found")

        # Convert rows to Stock objects
        stocks = []
        for row in rows:
            stock_data = json.loads(row[2]) if row[2] else []

            stocks.append(Stock(
                id=row[0],
                ticker=row[1],
                data=stock_data
            ))

        return stocks

    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/{ticker}", response_model=Stock)
async def get_stock(ticker: str):
    """Fetch stock data for a given ticker from the database."""
    try:
        # Connect to database
        db = get_db_connection()
        cursor = db.cursor()

        # Fetch stock by ticker
        cursor.execute('SELECT id, data FROM stocks WHERE ticker = ?;', (ticker,))
        row = cursor.fetchone()

        # If stock not found
        if not row:
            raise HTTPException(status_code=404, detail="Stock not found")

        # Parse stored JSON data
        stock_data = json.loads(row[1]) if row[1] else []

        return Stock(
            id=row[0],
            ticker=ticker,
            data=stock_data
        )

    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {err}")


@router.post("/", response_model=StockResponse, status_code=201)
async def create_stock(stock: StockCreate):
    """Fetch stock data from EODHD API and create a new stock entry in the database."""
    ticker = stock.ticker
    url = f"https://eodhd.com/api/eod/{ticker}?api_token={api_token}&fmt=json"

    try:
        # Fetch data from external API
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            eod_data = response.json()

        # Ensure data is list format
        if not isinstance(eod_data, list):
            eod_data = [eod_data]

        # Connect to database
        db = get_db_connection()
        cursor = db.cursor()

        # Check if stock already exists
        cursor.execute('SELECT 1 FROM stocks WHERE ticker = ?;', (ticker,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail=f"Stock {ticker} already exists. Use PUT /stocks/ to update."
            )

        # Insert new stock
        cursor.execute(
            'INSERT INTO stocks (ticker, data) VALUES (?, ?);',
            (ticker, json.dumps(eod_data))
        )
        db.commit()

        # Get inserted ID
        cursor.execute("SELECT id FROM stocks WHERE ticker = ?;", (ticker,))
        row = cursor.fetchone()

        return StockResponse(
            id=row[0] if row else 1,
            ticker=ticker,
            data=eod_data,
            message=f"Stock {ticker} created successfully."
        )

    except HTTPException:
        raise
    except httpx.RequestError as err:
        raise HTTPException(status_code=500, detail=f"Failed to fetch EOD data: {err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error creating stock: {err}")


@router.put("/", response_model=StockResponse)
async def update_stock(stock: StockUpdate):
    """Fetch stock data from EODHD API and update existing stock entry."""
    ticker = stock.ticker
    url = f"https://eodhd.com/api/eod/{ticker}?api_token={api_token}&fmt=json"

    try:
        # Fetch updated data from API
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            new_data = response.json()

        # Ensure list format
        if not isinstance(new_data, list):
            new_data = [new_data]

        # Connect to database
        db = get_db_connection()
        cursor = db.cursor()

        # Get existing stock
        cursor.execute('SELECT id, data FROM stocks WHERE ticker = ?;', (ticker,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Stock {ticker} not found. Use POST /stocks/ to create a new entry."
            )

        # Parse existing data
        existing_data = json.loads(row[1]) if row[1] else []
        existing_dates = {item["date"] for item in existing_data}

        # Merge new unique entries
        updated_data = existing_data.copy()
        new_dates = 0

        for item in new_data:
            if item["date"] not in existing_dates:
                updated_data.append(item)
                new_dates += 1

        # Sort by date
        updated_data.sort(key=lambda x: x["date"])

        # Update database
        cursor.execute(
            'UPDATE stocks SET data = ? WHERE ticker = ?;',
            (json.dumps(updated_data), ticker)
        )
        db.commit()

        return StockResponse(
            id=row[0],
            ticker=ticker,
            data=updated_data,
            message=(
                f"Stock {ticker} updated successfully. "
                + (f"Added {new_dates} new entries." if new_dates > 0 else "No new data to add.")
            )
        )

    except HTTPException:
        raise
    except httpx.RequestError as err:
        raise HTTPException(status_code=500, detail=f"Failed to fetch EOD data: {err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error updating stock: {err}")