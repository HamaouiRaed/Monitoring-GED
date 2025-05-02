from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os 
import logging


logging.basicConfig(level=logging.DEBUG)



# Initialize the database instance
db = SQLAlchemy()

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from the config object
    app.config.from_object("config.Config")

    # Initialize the database with the app
    db.init_app(app)

    # Register main routes
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register API routes
    from .routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    return app
