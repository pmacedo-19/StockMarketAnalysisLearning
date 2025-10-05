from flask import Blueprint, jsonify, request
from app.services import (
    fetch_and_store_stock_price, 
    get_filtered_stock_data, 
    get_latest_stock_prices, 
    get_stock_history,
    fetch_historical_data_from_finnhub,
    fetch_historical_data_yfinance,
    clear_cache,
    log_api_request
)
import time

stock_blueprint = Blueprint("stocks", __name__)

@stock_blueprint.route('/stock/<symbol>', methods=['GET'])
def get_stock_price(symbol):
    start_time = time.time()
    response = fetch_and_store_stock_price(symbol)
    log_api_request(endpoint=request.path, status_code=200 if isinstance(response, dict) else response[1], start_time=start_time)
    return jsonify(response)

@stock_blueprint.route('/stocks', methods=['GET'])
def get_stored_stock_data():
    start_time = time.time()
    symbol = request.args.get('symbol')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sort_by = request.args.get('sort_by', 'date')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    response = get_filtered_stock_data(symbol, start_date, end_date, sort_by, order, page, per_page)
    log_api_request(endpoint=request.path, status_code=200, start_time=start_time)
    return jsonify(response)

@stock_blueprint.route('/stocks/latest', methods=['GET'])
def get_latest_stocks():
    start_time = time.time()
    response = get_latest_stock_prices()
    log_api_request(endpoint=request.path, status_code=200, start_time=start_time)
    return jsonify(response)

@stock_blueprint.route('/stocks/history/<symbol>', methods=['GET'])
def get_stock_history_data(symbol):
    """
    Retrieves historical stock prices from the database.
    (This is separate from fetching from Finnhub directly.)
    """
    start_time = time.time()
    response = get_stock_history(symbol)
    log_api_request(endpoint=request.path, status_code=200 if isinstance(response, list) else response[1], start_time=start_time)
    return jsonify(response)

@stock_blueprint.route('/stocks/finnhub/history/<symbol>', methods=['GET'])
def get_finnhub_stock_history(symbol):
    """
    Fetches historical data directly from Finnhub's candle endpoint.
    Query Parameters:
      - resolution (optional): e.g., "D" (default), "W", "M"
      - start_date (optional): Format "YYYY-MM-DD"
      - end_date (optional): Format "YYYY-MM-DD"
    """
    start_time = time.time()
    resolution = request.args.get("resolution", "D")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    data = fetch_historical_data_from_finnhub(symbol, resolution, start_date, end_date)
    log_api_request(endpoint=request.path, status_code=200, start_time=start_time)
    return jsonify(data)

@stock_blueprint.route('/clear_cache', methods=['POST'])
def clear_cache_endpoint():
    start_time = time.time()
    response = clear_cache()
    log_api_request(endpoint=request.path, status_code=200, start_time=start_time)
    return jsonify(response)

@stock_blueprint.route('/stocks/yfinance/history/<symbol>', methods=['GET'])
def get_yfinance_stock_history(symbol):
    """
    Fetch historical stock data for a given symbol using yfinance.
    Query Parameters:
      - period (optional): Data period (default: "1mo")
      - interval (optional): Data interval (default: "1d")
    """
    start_time = time.time()
    period = request.args.get("period", "1mo")
    interval = request.args.get("interval", "1d")
    
    data = fetch_historical_data_yfinance(symbol, period, interval)
    log_api_request(endpoint=request.path, status_code=200, start_time=start_time)
    
    return jsonify(data)
