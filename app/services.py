from app import db, cache  # Import cache from __init__.py
import requests
from app.models import Stock, StockPrice
from datetime import datetime, timedelta, date
import os
from sqlalchemy import desc, asc
from app.models import db, APIRequestLog
from flask import request
import time

# Finnhub API details
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
FINNHUB_QUOTE_URL = "https://finnhub.io/api/v1/quote"
FINNHUB_STOCK_INFO_URL = "https://finnhub.io/api/v1/stock/profile2"

def get_stock_id(symbol):
    """Check if stock exists, fetch from API if missing."""
    stock = Stock.query.filter_by(symbol=symbol.upper()).first()
    if stock:
        return stock.id

    # Fetch stock metadata from Finnhub
    response = requests.get(f"{FINNHUB_STOCK_INFO_URL}?symbol={symbol}&token={FINNHUB_API_KEY}").json()
    if "name" not in response:
        return None  # Stock not found

    # Insert new stock into database
    new_stock = Stock(
        symbol=symbol.upper(),
        name=response.get("name"),
        sector=response.get("sector"),
        industry=response.get("finnhubIndustry")
    )
    db.session.add(new_stock)
    db.session.commit()
    return new_stock.id

@cache.memoize(timeout=300)  # Cache for 5 minutes (300 seconds)
def fetch_stock_price_from_api(symbol):
    """Fetch stock price from Finnhub and cache the response for 5 minutes."""
    response = requests.get(f"{FINNHUB_QUOTE_URL}?symbol={symbol}&token={FINNHUB_API_KEY}").json()

    if "c" not in response:
        return None  # API error or invalid symbol

    return {
        "open_price": response.get("o"),
        "high_price": response.get("h"),
        "low_price": response.get("l"),
        "close_price": response.get("c"),
        "volume": response.get("v", 0)
    }

def fetch_and_store_stock_price(symbol):
    """Fetch stock price from API, store it in database, and return cached data."""
    stock_id = get_stock_id(symbol)
    if not stock_id:
        return {"error": "Stock not found"}, 404

    # Fetch cached stock price
    stock_data = fetch_stock_price_from_api(symbol)
    if not stock_data:
        return {"error": "Invalid stock symbol or API error"}, 400

    # Store stock price in database (only if not already recorded today)
    existing_price = StockPrice.query.filter_by(stock_id=stock_id, date=date.today()).first()

    if existing_price:
        # Update existing price instead of inserting duplicate
        existing_price.open_price = stock_data["open_price"]
        existing_price.high_price = stock_data["high_price"]
        existing_price.low_price = stock_data["low_price"]
        existing_price.close_price = stock_data["close_price"]
        existing_price.volume = stock_data["volume"]
    else:
        # Insert new price record
        new_stock_price = StockPrice(
            stock_id=stock_id,
            date=date.today(),
            open_price=stock_data["open_price"],
            high_price=stock_data["high_price"],
            low_price=stock_data["low_price"],
            close_price=stock_data["close_price"],
            volume=stock_data["volume"]
        )
        db.session.add(new_stock_price)

    db.session.commit()

    return {
        "symbol": symbol,
        "date": str(date.today()),
        "open_price": stock_data["open_price"],
        "high_price": stock_data["high_price"],
        "low_price": stock_data["low_price"],
        "close_price": stock_data["close_price"],
        "volume": stock_data["volume"]
    }

def get_filtered_stock_data(symbol, start_date, end_date, sort_by, order, page, per_page):
    """Retrieve paginated, filtered, and sorted stock data."""
    
    query = StockPrice.query.join(Stock)

    # Apply filters
    if symbol:
        query = query.filter(Stock.symbol == symbol.upper())

    if start_date:
        query = query.filter(StockPrice.date >= start_date)

    if end_date:
        query = query.filter(StockPrice.date <= end_date)

    # Sorting logic
    sort_column_mapping = {
        "date": StockPrice.date,
        "open_price": StockPrice.open_price,
        "close_price": StockPrice.close_price,
        "volume": StockPrice.volume
    }

    if sort_by in sort_column_mapping:
        sort_column = sort_column_mapping[sort_by]
        query = query.order_by(asc(sort_column) if order == "asc" else desc(sort_column))
    else:
        query = query.order_by(desc(StockPrice.date))  # Default sort by date descending

    # Apply pagination
    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "total_records": paginated_query.total,
        "total_pages": paginated_query.pages,
        "current_page": page,
        "per_page": per_page,
        "stocks": [
            {
                "symbol": stock.stock.symbol,
                "date": str(stock.date),
                "open_price": stock.open_price,
                "high_price": stock.high_price,
                "low_price": stock.low_price,
                "close_price": stock.close_price,
                "volume": stock.volume
            }
            for stock in paginated_query.items
        ]
    }

def get_latest_stock_prices():
    """Retrieve the latest stock prices for all stored stocks."""
    stocks = db.session.query(
        Stock.symbol,
        StockPrice.date,
        StockPrice.open_price,
        StockPrice.high_price,
        StockPrice.low_price,
        StockPrice.close_price,
        StockPrice.volume
    ).join(StockPrice).order_by(StockPrice.date.desc()).distinct(Stock.symbol).all()

    return [
        {
            "symbol": stock.symbol,
            "date": str(stock.date),
            "open_price": stock.open_price,
            "high_price": stock.high_price,
            "low_price": stock.low_price,
            "close_price": stock.close_price,
            "volume": stock.volume
        }
        for stock in stocks
    ]

def get_stock_history(symbol):
    """Retrieve historical stock prices for a given symbol."""
    stock = Stock.query.filter_by(symbol=symbol.upper()).first()
    if not stock:
        return {"error": "Stock not found"}, 404

    history = StockPrice.query.filter_by(stock_id=stock.id).order_by(StockPrice.date.desc()).all()

    return [
        {
            "date": str(entry.date),
            "open_price": entry.open_price,
            "high_price": entry.high_price,
            "low_price": entry.low_price,
            "close_price": entry.close_price,
            "volume": entry.volume
        }
        for entry in history
    ]

def clear_cache():
    """Clears the cache for stock price requests."""
    cache.clear()
    return {"message": "Cache cleared successfully"}


def log_api_request(endpoint, status_code, start_time, user_id=None):
    """Logs API request details to the database."""
    response_time = int((time.time() - start_time) * 1000)  # Convert seconds to milliseconds

    log_entry = APIRequestLog(
        user_id=user_id,  # Currently None (can be used later for authentication)
        endpoint=endpoint,
        status_code=status_code,
        response_time_ms=response_time
    )

    db.session.add(log_entry)
    db.session.commit()