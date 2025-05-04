from datetime import timedelta
import os

class Config:
    # Secret key for sessions and CSRF protection
    SECRET_KEY = os.getenv("SECRET_KEY", "123456")

    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '1234567')  # JWT secret key for encoding/decoding tokens
    JWT_TOKEN_LOCATION = ['headers']  # JWT token is expected in headers
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # Token expiry (1 hour)

    # Set the debug mode based on the environment variable
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
    
    # Database URI (we'll load this from the .env file as well)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql://root:@localhost/monitoring_ged')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optional, disable unnecessary tracking
