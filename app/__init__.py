from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy and Cache
db = SQLAlchemy()
cache = Cache(config={'CACHE_TYPE': 'simple'})  # Uses in-memory caching

def create_app():
    """Application factory function to create a Flask app."""
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)

    # Register Blueprints
    from app.routes import stock_blueprint
    app.register_blueprint(stock_blueprint)

    return app
