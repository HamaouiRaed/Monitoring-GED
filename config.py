import os

class Config:
    # Secret key for sessions and CSRF protection
    SECRET_KEY = os.getenv("SECRET_KEY", "123456")

    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '1234567')  # JWT secret key for encoding/decoding tokens
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_NAME = os.getenv("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")
    JWT_COOKIE_SECURE = False  # True si tu utilises HTTPS
    JWT_COOKIE_CSRF_PROTECT = False

    # Set the debug mode based on the environment variable
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
    
    # Database URI (we'll load this from the .env file as well)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/monitoring_ged'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optional, disable unnecessary tracking
