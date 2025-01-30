import time
from flask import Blueprint, jsonify, request
from app.services import (
    fetch_and_store_stock_price, 
    get_filtered_stock_data, 
    get_latest_stock_prices, 
    get_stock_history, 
    clear_cache, 
    log_api_request
)

# Create a blueprint for stock-related routes
stock_blueprint = Blueprint("stocks", __name__)


@stock_blueprint.route('/stock/<symbol>', methods=['GET'])
def get_stock_price(symbol):
    """Fetches the latest stock price and logs the request."""
    start_time = time.time()
    response = fetch_and_store_stock_price(symbol)
    
    log_api_request(endpoint=request.path, status_code=200 if isinstance(response, dict) else response[1], start_time=start_time)
    return jsonify(response)


@stock_blueprint.route('/stocks', methods=['GET'])
def get_stored_stock_data():
    """Retrieves stored stock data with pagination, filtering, and sorting."""
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
    """Retrieves the latest stock prices for all stored stocks."""
    start_time = time.time()
    response = get_latest_stock_prices()
    log_api_request(endpoint=request.path, status_code=200, start_time=start_time)
    return jsonify(response)


@stock_blueprint.route('/stocks/history/<symbol>', methods=['GET'])
def get_stock_history_data(symbol):
    """Retrieves historical stock prices for a given symbol."""
    start_time = time.time()
    response = get_stock_history(symbol)
    
    log_api_request(endpoint=request.path, status_code=200 if isinstance(response, list) else response[1], start_time=start_time)
    return jsonify(response)


@stock_blueprint.route('/clear_cache', methods=['POST'])
def clear_cache_endpoint():
    """Clears the cache and logs the request."""
    start_time = time.time()
    response = clear_cache()
    log_api_request(endpoint=request.path, status_code=200, start_time=start_time)
    return jsonify(response)