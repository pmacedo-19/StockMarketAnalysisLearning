import os
import requests

API_KEY = os.getenv('FINNHUB_API_KEY')

def fetch_stock_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    response = requests.get(url)
    return response.json()
