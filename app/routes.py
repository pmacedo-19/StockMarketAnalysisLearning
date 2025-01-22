from flask import Blueprint, jsonify
from .services import fetch_stock_data

main = Blueprint('main', __name__)

@main.route('/stocks/<symbol>')
def get_stock_data(symbol):
    data = fetch_stock_data(symbol)
    return jsonify(data)
