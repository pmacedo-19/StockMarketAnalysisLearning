from app import db
from flask_sqlalchemy import SQLAlchemy

class User(db.Model):
    """User model to store registered users."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

class Stock(db.Model):
    """Stock model to store stock metadata."""
    __tablename__ = 'stocks'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100))
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))

class StockPrice(db.Model):
    """StockPrice model to store historical stock price data."""
    __tablename__ = 'stock_prices'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Numeric(10, 2))
    high_price = db.Column(db.Numeric(10, 2))
    low_price = db.Column(db.Numeric(10, 2))
    close_price = db.Column(db.Numeric(10, 2))
    volume = db.Column(db.BigInteger)

    stock = db.relationship('Stock', backref=db.backref('prices', lazy=True))

class APIRequestLog(db.Model):
    """APIRequestLog model to track API request usage and performance."""
    __tablename__ = 'api_request_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    endpoint = db.Column(db.String(255), nullable=False)
    request_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    status_code = db.Column(db.Integer)
    response_time_ms = db.Column(db.Integer)

    user = db.relationship('User', backref=db.backref('logs', lazy=True))
